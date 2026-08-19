from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from .geo import to_geojson
from .pipeline import AnalysisConfig, analyze_images
from .report import markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geochange", description="Explainable image change detection")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Compare a before/after image pair")
    analyze.add_argument("before", type=Path)
    analyze.add_argument("after", type=Path)
    analyze.add_argument("--output", type=Path, default=Path("geochange-output"))
    analyze.add_argument("--sensitivity", type=float, default=3.5)
    analyze.add_argument("--min-area", type=int, default=24)
    analyze.add_argument("--max-shift", type=int, default=12)
    analyze.add_argument("--bounds", type=float, nargs=4, metavar=("W", "S", "E", "N"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "analyze":
        return 1
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    before = Image.open(args.before).convert("RGB")
    after = Image.open(args.after).convert("RGB")
    result, overlay, mask, aligned = analyze_images(
        before,
        after,
        AnalysisConfig(args.max_shift, args.sensitivity, args.min_area),
    )
    Image.fromarray(overlay).save(output / "overlay.png")
    Image.fromarray((mask * 255).astype("uint8")).save(output / "mask.png")
    Image.fromarray(aligned).save(output / "aligned-after.png")
    (output / "result.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    (output / "changes.geojson").write_text(
        json.dumps(to_geojson(result, args.bounds), indent=2), encoding="utf-8"
    )
    (output / "report.md").write_text(markdown_report(result), encoding="utf-8")
    print(f"Detected {len(result.regions)} region(s); results written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

