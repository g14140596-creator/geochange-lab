from __future__ import annotations

import numpy as np


def to_gray(image: np.ndarray) -> np.ndarray:
    rgb = image.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def _overlap(reference: np.ndarray, moving: np.ndarray, dx: int, dy: int):
    height, width = reference.shape[:2]
    x0 = max(0, -dx)
    x1 = min(width, width - dx)
    y0 = max(0, -dy)
    y1 = min(height, height - dy)
    if x1 <= x0 or y1 <= y0:
        return None
    return (
        reference[y0:y1, x0:x1],
        moving[y0 + dy : y1 + dy, x0 + dx : x1 + dx],
    )


def estimate_translation(
    reference: np.ndarray,
    moving: np.ndarray,
    max_shift: int = 12,
    sample_step: int = 2,
) -> tuple[int, int, float, float]:
    """Estimate integer translation with robust mean absolute error.

    ``dx`` and ``dy`` describe how far content in ``moving`` is displaced from
    the reference. Positive ``dx`` means the same feature appears farther right.
    """
    ref_gray = to_gray(reference)
    mov_gray = to_gray(moving)
    baseline = float(np.mean(np.abs(ref_gray - mov_gray)) / 255.0)
    best = (0, 0, baseline)

    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            pair = _overlap(ref_gray, mov_gray, dx, dy)
            if pair is None:
                continue
            ref_crop, mov_crop = pair
            ref_crop = ref_crop[::sample_step, ::sample_step]
            mov_crop = mov_crop[::sample_step, ::sample_step]
            error = float(np.mean(np.abs(ref_crop - mov_crop)) / 255.0)
            # Tiny regularizer avoids choosing a large shift for a negligible gain.
            objective = error + 0.00015 * (abs(dx) + abs(dy))
            if objective < best[2] + 0.00015 * (abs(best[0]) + abs(best[1])):
                best = (dx, dy, error)
    return best[0], best[1], baseline, best[2]


def align_image(moving: np.ndarray, dx: int, dy: int) -> tuple[np.ndarray, np.ndarray]:
    """Move an image into the reference coordinate system and return a valid mask."""
    height, width = moving.shape[:2]
    aligned = np.zeros_like(moving)
    valid = np.zeros((height, width), dtype=bool)
    x0 = max(0, -dx)
    x1 = min(width, width - dx)
    y0 = max(0, -dy)
    y1 = min(height, height - dy)
    aligned[y0:y1, x0:x1] = moving[y0 + dy : y1 + dy, x0 + dx : x1 + dx]
    valid[y0:y1, x0:x1] = True
    return aligned, valid

