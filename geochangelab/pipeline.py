from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from .alignment import align_image, estimate_translation
from .models import Alignment, AnalysisResult
from .segmentation import adaptive_threshold, change_score, extract_regions


@dataclass(frozen=True)
class AnalysisConfig:
    max_shift: int = 12
    sensitivity: float = 3.5
    min_area: int = 24


def _as_rgb_array(image: Image.Image | np.ndarray) -> np.ndarray:
    if isinstance(image, Image.Image):
        return np.asarray(image.convert("RGB"), dtype=np.uint8)
    array = np.asarray(image, dtype=np.uint8)
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("Images must be RGB arrays with shape (height, width, 3)")
    return array


def analyze_images(
    before: Image.Image | np.ndarray,
    after: Image.Image | np.ndarray,
    config: AnalysisConfig | None = None,
) -> tuple[AnalysisResult, np.ndarray, np.ndarray, np.ndarray]:
    """Run registration, scoring, segmentation and region explanation.

    Returns ``(result, overlay, mask, aligned_after)``.
    """
    cfg = config or AnalysisConfig()
    reference = _as_rgb_array(before)
    moving = _as_rgb_array(after)
    if reference.shape != moving.shape:
        raise ValueError("Before and after images must have the same dimensions")

    dx, dy, mae_before, mae_after = estimate_translation(reference, moving, cfg.max_shift)
    aligned, valid = align_image(moving, dx, dy)
    score = change_score(reference, aligned)
    threshold = adaptive_threshold(score, valid, cfg.sensitivity)
    raw_mask = (score >= threshold) & valid
    mask, regions = extract_regions(raw_mask, score, cfg.min_area)

    overlay = make_overlay(aligned, mask, regions)
    changed_pixels = int(mask.sum())
    height, width = mask.shape
    result = AnalysisResult(
        width=width,
        height=height,
        threshold=round(threshold, 4),
        changed_pixels=changed_pixels,
        changed_ratio=round(changed_pixels / (height * width), 6),
        alignment=Alignment(dx, dy, round(mae_before, 5), round(mae_after, 5)),
        regions=regions,
    )
    return result, overlay, mask, aligned


def make_overlay(aligned: np.ndarray, mask: np.ndarray, regions) -> np.ndarray:
    canvas = aligned.astype(np.float32).copy()
    red = np.zeros_like(canvas)
    red[..., 0] = 255
    canvas[mask] = 0.46 * canvas[mask] + 0.54 * red[mask]
    image = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(image)
    colors = {"low": "#F5B700", "medium": "#FF7A45", "high": "#FF3B30"}
    for region in regions:
        x0, y0, x1, y1 = region.bbox
        color = colors[region.severity]
        draw.rectangle((x0, y0, x1, y1), outline=color, width=2)
        draw.text((x0 + 3, y0 + 3), f"#{region.id} {region.severity}", fill=color)
    return np.asarray(image)

