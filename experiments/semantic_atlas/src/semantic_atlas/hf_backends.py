from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class QwenEmbedder:
    model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    truncate_dim: int | None = None

    def __post_init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("install semantic-atlas-toy[models]") from exc
        self.model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        kwargs = {"convert_to_numpy": True, "normalize_embeddings": True}
        if self.truncate_dim is not None:
            kwargs["truncate_dim"] = self.truncate_dim
        return np.asarray(self.model.encode(texts, **kwargs), dtype=np.float64)


@dataclass
class QwenGenerator:
    model_name: str = "Qwen/Qwen3-0.6B"
    max_new_tokens: int = 32
    temperature: float = 0.8

    def __post_init__(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("install semantic-atlas-toy[models]") from exc

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )

    def propose(self, prefix: str, count: int) -> list[tuple[str, float]]:
        inputs = self.tokenizer(prefix, return_tensors="pt").to(self.model.device)
        with self.torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=self.temperature,
                num_return_sequences=count,
                return_dict_in_generate=True,
                output_scores=True,
            )

        prompt_tokens = inputs["input_ids"].shape[1]
        continuations = outputs.sequences[:, prompt_tokens:]
        transition_scores = self.model.compute_transition_scores(
            outputs.sequences,
            outputs.scores,
            normalize_logits=True,
        )
        results: list[tuple[str, float]] = []
        for ids, token_scores in zip(continuations, transition_scores, strict=True):
            text = self.tokenizer.decode(ids, skip_special_tokens=True)
            results.append((text, float(token_scores.sum().item())))
        return results
