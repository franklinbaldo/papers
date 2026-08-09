from __future__ import annotations

from typing import Any

import numpy as np

from .compiled import WeightJacobianOperator


def compile_qwen_expected_next_operator(
    generator: Any,
    prefix: str,
    srf_projection: np.ndarray,
    temperature: float = 1.0,
) -> WeightJacobianOperator:
    """Compile a local next-semantic Jacobian from frozen Qwen weights.

    This uses a differentiable one-step relaxation rather than observed trajectories:
    the current prefix is run through the frozen transformer, next-token logits are
    converted to a soft expected token embedding, that embedding is appended, and the
    transformer is run one additional step. The final hidden state is projected into
    the frozen SRF. Autograd then linearizes this entire weight-derived map around the
    final input embedding of the prefix.

    The soft-token relaxation is an approximation that must be evaluated against
    discrete empirical transitions; it is not trained on `(state, next_state)` pairs.
    """
    if temperature <= 0:
        raise ValueError("temperature must be positive")

    torch = generator.torch
    model = generator.model
    tokenizer = generator.tokenizer
    model.eval()

    encoded = tokenizer(prefix, return_tensors="pt")
    input_ids = encoded["input_ids"].to(model.device)
    embedding_layer = model.get_input_embeddings()
    base_embeddings = embedding_layer(input_ids).detach()
    fixed_prefix = base_embeddings[:, :-1, :].detach()
    anchor = base_embeddings[:, -1, :].squeeze(0).detach()

    projection = torch.as_tensor(
        np.asarray(srf_projection),
        device=anchor.device,
        dtype=anchor.dtype,
    )
    if projection.ndim != 2 or projection.shape[1] != anchor.shape[0]:
        raise ValueError("srf_projection must have shape [srf_dim, hidden_dim]")

    token_embedding_weight = embedding_layer.weight

    def transition(last_input_embedding):
        current_embeddings = torch.cat(
            [fixed_prefix, last_input_embedding.reshape(1, 1, -1)], dim=1
        )
        current = model(
            inputs_embeds=current_embeddings,
            use_cache=False,
            output_hidden_states=True,
            return_dict=True,
        )
        logits = current.logits[0, -1]
        probabilities = torch.softmax(logits / temperature, dim=-1)
        expected_next_embedding = probabilities @ token_embedding_weight

        augmented_embeddings = torch.cat(
            [current_embeddings, expected_next_embedding.reshape(1, 1, -1)], dim=1
        )
        next_step = model(
            inputs_embeds=augmented_embeddings,
            use_cache=False,
            output_hidden_states=True,
            return_dict=True,
        )
        next_hidden = next_step.hidden_states[-1][0, -1]
        return projection @ next_hidden

    return WeightJacobianOperator.from_torch_transition(transition, anchor)
