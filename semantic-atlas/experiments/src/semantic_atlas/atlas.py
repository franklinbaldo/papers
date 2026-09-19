from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Transition:
    source: int
    target: int
    count: int = 0
    mean_distance: float = 0.0
    mean_turning_cost: float = 0.0

    def observe(self, distance: float, turning_cost: float = 0.0) -> None:
        self.count += 1
        self.mean_distance += (distance - self.mean_distance) / self.count
        self.mean_turning_cost += (turning_cost - self.mean_turning_cost) / self.count

    @property
    def natural_cost(self) -> float:
        frequency_penalty = 1.0 / np.sqrt(max(self.count, 1))
        return float(self.mean_distance + self.mean_turning_cost + frequency_penalty)


@dataclass
class SemanticCell:
    cell_id: int
    center: np.ndarray
    count: int = 0
    mean_radius: float = 0.0
    escape_observations: list[float] = field(default_factory=list)

    def observe(self, point: np.ndarray) -> None:
        distance = float(np.linalg.norm(point - self.center))
        self.count += 1
        self.mean_radius += (distance - self.mean_radius) / self.count

    @property
    def density(self) -> float:
        return float(self.count / max(self.mean_radius, 1e-6))

    def escape_cost(self, quantile: float = 0.5) -> float | None:
        if not self.escape_observations:
            return None
        return float(np.quantile(self.escape_observations, quantile))


class SemanticAtlas:
    """Small graph atlas with deterministic nearest-center assignment.

    Cell centers are deliberately supplied externally. The first experiment uses
    centers learned from a frozen calibration corpus; more sophisticated adaptive
    partitioning belongs in later work.
    """

    def __init__(self, centers: np.ndarray):
        centers = np.asarray(centers, dtype=np.float64)
        if centers.ndim != 2 or len(centers) == 0:
            raise ValueError("centers must be a non-empty [cells, dim] array")
        self.cells = [SemanticCell(i, center.copy()) for i, center in enumerate(centers)]
        self.transitions: dict[tuple[int, int], Transition] = {}

    @property
    def centers(self) -> np.ndarray:
        return np.stack([cell.center for cell in self.cells])

    def assign(self, points: np.ndarray) -> np.ndarray:
        points = np.atleast_2d(np.asarray(points, dtype=np.float64))
        distances = np.linalg.norm(points[:, None, :] - self.centers[None, :, :], axis=-1)
        return np.argmin(distances, axis=1)

    def observe_path(self, path: np.ndarray) -> np.ndarray:
        path = np.asarray(path, dtype=np.float64)
        ids = self.assign(path)
        for point, cell_id in zip(path, ids, strict=True):
            self.cells[int(cell_id)].observe(point)
        for i in range(len(path) - 1):
            source, target = int(ids[i]), int(ids[i + 1])
            key = (source, target)
            transition = self.transitions.setdefault(key, Transition(source=source, target=target))
            transition.observe(float(np.linalg.norm(path[i + 1] - path[i])))
        return ids

    def neighbors(self, cell_id: int) -> list[Transition]:
        return sorted(
            (edge for (source, _), edge in self.transitions.items() if source == cell_id),
            key=lambda edge: edge.natural_cost,
        )

    def shortest_path(self, start: int, goal: int) -> tuple[float, list[int]]:
        """Dijkstra over observed directed transitions."""
        unvisited = {cell.cell_id for cell in self.cells}
        distance = {cell.cell_id: float("inf") for cell in self.cells}
        previous: dict[int, int] = {}
        distance[start] = 0.0

        while unvisited:
            current = min(unvisited, key=distance.__getitem__)
            if current == goal or not np.isfinite(distance[current]):
                break
            unvisited.remove(current)
            for edge in self.neighbors(current):
                if edge.target not in unvisited:
                    continue
                candidate = distance[current] + edge.natural_cost
                if candidate < distance[edge.target]:
                    distance[edge.target] = candidate
                    previous[edge.target] = current

        if not np.isfinite(distance[goal]):
            return float("inf"), []

        path = [goal]
        while path[-1] != start:
            path.append(previous[path[-1]])
        path.reverse()
        return distance[goal], path
