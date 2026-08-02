from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


def _normalize(x: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.clip(norm, 1e-12, None)


def _gini(counts: np.ndarray) -> float:
    counts = np.asarray(counts, dtype=float)
    if counts.sum() == 0:
        return 0.0
    values = np.sort(counts)
    n = len(values)
    cumulative = np.cumsum(values)
    return float((n + 1 - 2 * cumulative.sum() / cumulative[-1]) / n)


@dataclass(frozen=True)
class EnvConfig:
    n_contexts: int = 16
    chunks_per_context: int = 4
    dim: int = 32
    query_noise: float = 0.08
    key_noise: float = 0.12
    seed: int = 0


class SyntheticChunkEnv:
    """Contextual bandit with semantic siblings and one useful chunk.

    Each context owns several chunks that are semantically close. Exactly one
    sibling is functionally useful. Cosine search has high candidate recall but
    cannot reliably identify that sibling without reward-conditioned learning.
    """

    def __init__(self, config: EnvConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.prototypes = _normalize(
            self.rng.normal(size=(config.n_contexts, config.dim))
        )

        semantic_keys: list[np.ndarray] = []
        chunk_contexts: list[int] = []
        for context in range(config.n_contexts):
            for _ in range(config.chunks_per_context):
                key = self.prototypes[context] + config.key_noise * self.rng.normal(
                    size=config.dim
                )
                semantic_keys.append(key)
                chunk_contexts.append(context)

        self.semantic_keys = _normalize(np.stack(semantic_keys))
        self.chunk_contexts = np.asarray(chunk_contexts, dtype=int)
        self.n_chunks = len(self.chunk_contexts)

        # Functional utility is deliberately independent of nearest-cosine rank.
        self.best_chunk = np.empty(config.n_contexts, dtype=int)
        for context in range(config.n_contexts):
            start = context * config.chunks_per_context
            offset = int(self.rng.integers(config.chunks_per_context))
            self.best_chunk[context] = start + offset

    def sample(self, rng: np.random.Generator) -> tuple[int, np.ndarray]:
        context = int(rng.integers(self.config.n_contexts))
        query = self.prototypes[context] + self.config.query_noise * rng.normal(
            size=self.config.dim
        )
        return context, _normalize(query[None, :])[0]

    def reward(self, context: int, chunk: int) -> float:
        return float(chunk == self.best_chunk[context])

    def semantic_topk(self, query: np.ndarray, top_k: int) -> np.ndarray:
        scores = self.semantic_keys @ query
        k = min(top_k, self.n_chunks)
        return np.argpartition(scores, -k)[-k:]


class Retriever(Protocol):
    name: str

    def select(
        self,
        context: int,
        query: np.ndarray,
        candidates: np.ndarray,
        training: bool,
        rng: np.random.Generator,
    ) -> int: ...

    def update(
        self,
        context: int,
        query: np.ndarray,
        candidates: np.ndarray,
        chosen: int,
        reward: float,
    ) -> None: ...

    @property
    def selection_counts(self) -> np.ndarray: ...


class BaseRetriever:
    def __init__(self, semantic_keys: np.ndarray):
        self.semantic_keys = semantic_keys.copy()
        self._selection_counts = np.zeros(len(semantic_keys), dtype=int)

    @property
    def selection_counts(self) -> np.ndarray:
        return self._selection_counts


class CosineOnlyRetriever(BaseRetriever):
    name = "cosine_only"

    def select(self, context, query, candidates, training, rng):
        scores = self.semantic_keys[candidates] @ query
        chosen = int(candidates[int(np.argmax(scores))])
        self._selection_counts[chosen] += 1
        return chosen

    def update(self, context, query, candidates, chosen, reward):
        return None


class SelectionPromotionRetriever(BaseRetriever):
    """Naive popularity feedback: selected chunks rise regardless of reward."""

    name = "selection_promotion"

    def __init__(self, semantic_keys: np.ndarray, beta: float = 0.25):
        super().__init__(semantic_keys)
        self.beta = beta
        self.popularity = np.zeros(len(semantic_keys), dtype=float)

    def select(self, context, query, candidates, training, rng):
        semantic = self.semantic_keys[candidates] @ query
        bonus = self.beta * np.log1p(self.popularity[candidates])
        scores = semantic + bonus
        chosen = int(candidates[int(np.argmax(scores))])
        self._selection_counts[chosen] += 1
        return chosen

    def update(self, context, query, candidates, chosen, reward):
        self.popularity[chosen] += 1.0


class RewardConditionedRetriever(BaseRetriever):
    name = "reward_conditioned"

    def __init__(
        self,
        semantic_keys: np.ndarray,
        n_contexts: int,
        *,
        alpha: float = 0.35,
        beta: float = 0.35,
        gamma: float = 0.9,
        exploration: float = 0.35,
        lr_key: float = 0.08,
        lr_utility: float = 0.12,
        lr_value: float = 0.05,
    ):
        super().__init__(semantic_keys)
        self.functional_keys = semantic_keys.copy()
        self.utility = np.zeros((n_contexts, len(semantic_keys)), dtype=float)
        self.value = np.zeros(n_contexts, dtype=float)
        self.exposures = np.zeros(len(semantic_keys), dtype=int)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.exploration = exploration
        self.lr_key = lr_key
        self.lr_utility = lr_utility
        self.lr_value = lr_value
        self.total_steps = 0

    def select(self, context, query, candidates, training, rng):
        semantic = self.semantic_keys[candidates] @ query
        functional = self.functional_keys[candidates] @ query
        utility = self.utility[context, candidates]
        if training:
            ucb = self.exploration * np.sqrt(
                np.log(self.total_steps + 2.0) / (self.exposures[candidates] + 1.0)
            )
        else:
            ucb = 0.0
        scores = (
            self.alpha * semantic
            + self.beta * functional
            + self.gamma * utility
            + ucb
        )
        max_score = np.max(scores)
        tied = np.flatnonzero(np.isclose(scores, max_score))
        local_index = int(rng.choice(tied)) if training else int(tied[0])
        chosen = int(candidates[local_index])
        self._selection_counts[chosen] += 1
        if training:
            self.exposures[candidates] += 1
            self.total_steps += 1
        return chosen

    def update(self, context, query, candidates, chosen, reward):
        advantage = reward - self.value[context]
        self.value[context] += self.lr_value * advantage
        self.utility[context, chosen] += self.lr_utility * (
            advantage - self.utility[context, chosen]
        )
        self.functional_keys[chosen] = _normalize(
            (self.functional_keys[chosen] + self.lr_key * advantage * query)[None, :]
        )[0]


@dataclass
class RunMetrics:
    method: str
    seed: int
    train_reward: float
    eval_reward: float
    eval_regret: float
    eval_best_chunk_rate: float
    candidate_recall: float
    selection_gini: float
    max_selection_share: float

    def as_dict(self) -> dict[str, float | int | str]:
        return self.__dict__.copy()


def _build_retriever(name: str, env: SyntheticChunkEnv) -> Retriever:
    if name == "cosine_only":
        return CosineOnlyRetriever(env.semantic_keys)
    if name == "selection_promotion":
        return SelectionPromotionRetriever(env.semantic_keys)
    if name == "reward_conditioned":
        return RewardConditionedRetriever(env.semantic_keys, env.config.n_contexts)
    raise ValueError(f"Unknown method: {name}")


def _run_phase(
    env: SyntheticChunkEnv,
    retriever: Retriever,
    episodes: int,
    top_k: int,
    *,
    training: bool,
    seed: int,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    rewards = 0.0
    best_hits = 0
    candidate_hits = 0

    for _ in range(episodes):
        context, query = env.sample(rng)
        candidates = env.semantic_topk(query, top_k)
        best = int(env.best_chunk[context])
        candidate_hits += int(best in candidates)
        chosen = retriever.select(context, query, candidates, training, rng)
        reward = env.reward(context, chosen)
        rewards += reward
        best_hits += int(chosen == best)
        if training:
            retriever.update(context, query, candidates, chosen, reward)

    denom = max(episodes, 1)
    return rewards / denom, best_hits / denom, candidate_hits / denom


def run_one(
    method: str,
    seed: int,
    train_episodes: int,
    eval_episodes: int,
    top_k: int,
    env_config: EnvConfig,
) -> RunMetrics:
    config = EnvConfig(**{**env_config.__dict__, "seed": seed})
    env = SyntheticChunkEnv(config)
    retriever = _build_retriever(method, env)

    train_reward, _, _ = _run_phase(
        env,
        retriever,
        train_episodes,
        top_k,
        training=True,
        seed=seed + 10_000,
    )
    before_eval_counts = retriever.selection_counts.copy()
    eval_reward, eval_best, candidate_recall = _run_phase(
        env,
        retriever,
        eval_episodes,
        top_k,
        training=False,
        seed=seed + 20_000,
    )
    eval_counts = retriever.selection_counts - before_eval_counts
    max_share = float(eval_counts.max() / max(eval_counts.sum(), 1))

    return RunMetrics(
        method=method,
        seed=seed,
        train_reward=train_reward,
        eval_reward=eval_reward,
        eval_regret=1.0 - eval_reward,
        eval_best_chunk_rate=eval_best,
        candidate_recall=candidate_recall,
        selection_gini=_gini(eval_counts),
        max_selection_share=max_share,
    )


def summarize(rows: list[RunMetrics]) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    for method in sorted({row.method for row in rows}):
        group = [row for row in rows if row.method == method]
        summary.append(
            {
                "method": method,
                "eval_reward_mean": float(np.mean([r.eval_reward for r in group])),
                "eval_reward_std": float(np.std([r.eval_reward for r in group])),
                "candidate_recall_mean": float(
                    np.mean([r.candidate_recall for r in group])
                ),
                "selection_gini_mean": float(
                    np.mean([r.selection_gini for r in group])
                ),
                "max_selection_share_mean": float(
                    np.mean([r.max_selection_share for r in group])
                ),
            }
        )
    return summary


def write_outputs(
    output_dir: Path,
    rows: list[RunMetrics],
    summary: list[dict[str, float | str]],
    config: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].as_dict()))
        writer.writeheader()
        writer.writerows(row.as_dict() for row in rows)

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump({"config": config, "summary": summary}, handle, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthetic reward-conditioned retrieval experiment"
    )
    parser.add_argument("--train-episodes", type=int, default=8_000)
    parser.add_argument("--eval-episodes", type=int, default=2_000)
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--n-contexts", type=int, default=16)
    parser.add_argument("--chunks-per-context", type=int, default=4)
    parser.add_argument("--dim", type=int, default=32)
    parser.add_argument("--output", type=Path, default=Path("results"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    methods = ("cosine_only", "selection_promotion", "reward_conditioned")
    env_config = EnvConfig(
        n_contexts=args.n_contexts,
        chunks_per_context=args.chunks_per_context,
        dim=args.dim,
    )
    rows = [
        run_one(
            method,
            seed,
            args.train_episodes,
            args.eval_episodes,
            args.top_k,
            env_config,
        )
        for seed in range(args.seeds)
        for method in methods
    ]
    aggregate = summarize(rows)
    config = {
        "train_episodes": args.train_episodes,
        "eval_episodes": args.eval_episodes,
        "seeds": args.seeds,
        "top_k": args.top_k,
        "n_contexts": args.n_contexts,
        "chunks_per_context": args.chunks_per_context,
        "dim": args.dim,
    }
    write_outputs(args.output, rows, aggregate, config)
    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()
