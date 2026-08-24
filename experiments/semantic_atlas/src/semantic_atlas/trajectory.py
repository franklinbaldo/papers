from __future__ import annotations

import numpy as np


def _safe_norm(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return np.maximum(np.linalg.norm(x, axis=axis), 1e-12)


def turning_angles(path: np.ndarray) -> np.ndarray:
    path = np.asarray(path, dtype=np.float64)
    if len(path) < 3:
        return np.empty(0, dtype=np.float64)
    velocity = np.diff(path, axis=0)
    a = velocity[:-1]
    b = velocity[1:]
    cosine = np.sum(a * b, axis=1) / (_safe_norm(a) * _safe_norm(b))
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def trajectory_metrics(path: np.ndarray, goal: np.ndarray | None = None) -> dict[str, float]:
    path = np.asarray(path, dtype=np.float64)
    if path.ndim != 2 or len(path) < 1:
        raise ValueError("path must be a non-empty [steps, dim] array")

    steps = np.diff(path, axis=0)
    step_lengths = _safe_norm(steps) if len(steps) else np.empty(0)
    length = float(step_lengths.sum())
    displacement = float(np.linalg.norm(path[-1] - path[0]))
    angles = turning_angles(path)

    result = {
        "path_length": length,
        "displacement": displacement,
        "straightness": displacement / max(length, 1e-12),
        "mean_turning_angle": float(angles.mean()) if len(angles) else 0.0,
        "max_turning_angle": float(angles.max()) if len(angles) else 0.0,
    }

    if goal is not None:
        goal = np.asarray(goal, dtype=np.float64)
        initial = float(np.linalg.norm(path[0] - goal))
        final = float(np.linalg.norm(path[-1] - goal))
        result.update(
            initial_goal_distance=initial,
            final_goal_distance=final,
            goal_progress=initial - final,
        )
    return result


def route_progress(path: np.ndarray, waypoint: np.ndarray) -> float:
    path = np.asarray(path, dtype=np.float64)
    waypoint = np.asarray(waypoint, dtype=np.float64)
    if len(path) < 2:
        return 0.0
    return float(np.linalg.norm(path[0] - waypoint) - np.linalg.norm(path[-1] - waypoint))
