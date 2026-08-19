from __future__ import annotations

from collections import deque

import numpy as np

from .alignment import to_gray
from .models import ChangeRegion


def _box_blur(array: np.ndarray) -> np.ndarray:
    padded = np.pad(array, 1, mode="edge")
    total = np.zeros_like(array, dtype=np.float32)
    for row in range(3):
        for col in range(3):
            total += padded[row : row + array.shape[0], col : col + array.shape[1]]
    return total / 9.0


def change_score(reference: np.ndarray, aligned: np.ndarray) -> np.ndarray:
    """Fuse color and edge changes into a normalized, interpretable score map."""
    color_delta = np.mean(
        np.abs(reference.astype(np.float32) - aligned.astype(np.float32)), axis=2
    ) / 255.0
    ref_gray = to_gray(reference)
    mov_gray = to_gray(aligned)
    ref_gy, ref_gx = np.gradient(ref_gray)
    mov_gy, mov_gx = np.gradient(mov_gray)
    ref_edge = np.hypot(ref_gx, ref_gy)
    mov_edge = np.hypot(mov_gx, mov_gy)
    edge_delta = np.clip(np.abs(ref_edge - mov_edge) / 255.0, 0.0, 1.0)
    return np.clip(_box_blur(0.76 * color_delta + 0.24 * edge_delta), 0.0, 1.0)


def adaptive_threshold(score: np.ndarray, valid: np.ndarray, sensitivity: float = 3.5) -> float:
    values = score[valid]
    if values.size == 0:
        return 1.0
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    robust_sigma = 1.4826 * mad
    return float(np.clip(median + sensitivity * max(robust_sigma, 0.012), 0.075, 0.45))


def extract_regions(
    mask: np.ndarray,
    score: np.ndarray,
    min_area: int,
) -> tuple[np.ndarray, tuple[ChangeRegion, ...]]:
    """Connected-component labeling without a heavyweight vision dependency."""
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    cleaned = np.zeros_like(mask, dtype=bool)
    regions: list[ChangeRegion] = []
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))

    for start_y, start_x in zip(*np.where(mask & ~visited)):
        if visited[start_y, start_x]:
            continue
        queue = deque([(int(start_y), int(start_x))])
        visited[start_y, start_x] = True
        pixels: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            for step_y, step_x in neighbors:
                ny, nx = y + step_y, x + step_x
                if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((ny, nx))
        if len(pixels) < min_area:
            continue

        ys = np.array([p[0] for p in pixels])
        xs = np.array([p[1] for p in pixels])
        cleaned[ys, xs] = True
        values = score[ys, xs]
        impact = len(pixels) / (height * width) * float(np.mean(values))
        severity = "high" if impact >= 0.02 else "medium" if impact >= 0.004 else "low"
        regions.append(
            ChangeRegion(
                id=len(regions) + 1,
                area_pixels=len(pixels),
                bbox=(int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1),
                centroid=(round(float(xs.mean()), 2), round(float(ys.mean()), 2)),
                mean_score=round(float(np.mean(values)), 4),
                max_score=round(float(np.max(values)), 4),
                severity=severity,
            )
        )
    regions.sort(key=lambda item: item.area_pixels, reverse=True)
    # IDs follow the final importance order.
    normalized = tuple(
        ChangeRegion(i + 1, r.area_pixels, r.bbox, r.centroid, r.mean_score, r.max_score, r.severity)
        for i, r in enumerate(regions)
    )
    return cleaned, normalized

