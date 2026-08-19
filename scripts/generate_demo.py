from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geochangelab.geo import to_geojson
from geochangelab.pipeline import AnalysisConfig, analyze_images
from geochangelab.report import markdown_report


def scene() -> tuple[Image.Image, Image.Image]:
    rng = np.random.default_rng(7)
    base = np.zeros((420, 640, 3), dtype=np.uint8)
    base[:] = (104, 139, 91)
    noise = rng.normal(0, 5, base.shape[:2])[..., None]
    base = np.clip(base + noise, 0, 255).astype(np.uint8)
    before = Image.fromarray(base)
    draw = ImageDraw.Draw(before)
    draw.polygon([(0, 95), (640, 135), (640, 170), (0, 130)], fill=(80, 88, 92))
    draw.rectangle((70, 210, 230, 350), fill=(126, 110, 78))
    for x in range(92, 220, 34):
        for y in range(228, 340, 31):
            draw.ellipse((x, y, x + 10, y + 10), fill=(42, 88, 48))
    draw.polygon([(390, 235), (515, 205), (550, 315), (418, 338)], fill=(74, 119, 142))
    after = before.copy()
    draw_after = ImageDraw.Draw(after)
    draw_after.rectangle((260, 190, 378, 280), fill=(214, 211, 197), outline=(235, 235, 228), width=5)
    draw_after.rectangle((280, 215, 305, 245), fill=(105, 118, 128))
    draw_after.rectangle((330, 215, 355, 245), fill=(105, 118, 128))
    draw_after.polygon([(405, 220), (530, 190), (566, 306), (430, 332)], fill=(65, 135, 165))
    return before, after


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "examples"
    output.mkdir(exist_ok=True)
    before, after = scene()
    result, overlay, mask, aligned = analyze_images(
        before, after, AnalysisConfig(max_shift=0, sensitivity=3.2, min_area=45)
    )
    before.save(output / "before.png")
    after.save(output / "after.png")
    Image.fromarray(overlay).save(output / "overlay.png")
    Image.fromarray((mask * 255).astype(np.uint8)).save(output / "mask.png")
    Image.fromarray(aligned).save(output / "aligned-after.png")
    (output / "result.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    (output / "changes.geojson").write_text(json.dumps(to_geojson(result), indent=2), encoding="utf-8")
    (output / "report.md").write_text(markdown_report(result), encoding="utf-8")
    # Build a README-ready visual summary without external design dependencies.
    cards = [("BEFORE", before), ("AFTER", after), ("EXPLAINABLE OVERLAY", Image.fromarray(overlay))]
    card_width, card_height, gap, margin, label_height = 640, 420, 22, 34, 62
    triptych = Image.new(
        "RGB",
        (margin * 2 + card_width * 3 + gap * 2, margin * 2 + label_height + card_height),
        (244, 247, 242),
    )
    triptych_draw = ImageDraw.Draw(triptych)
    font = ImageFont.load_default(size=22)
    for index, (label, card) in enumerate(cards):
        x = margin + index * (card_width + gap)
        triptych.paste(card, (x, margin + label_height))
        triptych_draw.rounded_rectangle(
            (x, margin, x + card_width, margin + label_height - 10),
            radius=12,
            fill=(16, 35, 31),
        )
        triptych_draw.text((x + 20, margin + 13), label, fill=(185, 231, 105), font=font)
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    triptych.save(docs / "demo-triptych.png", optimize=True)
    print(f"Demo written to {output}; {len(result.regions)} region(s) detected")


if __name__ == "__main__":
    main()
