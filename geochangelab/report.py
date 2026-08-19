from __future__ import annotations

from .models import AnalysisResult


def markdown_report(result: AnalysisResult) -> str:
    alignment_gain = result.alignment.mae_before - result.alignment.mae_after
    lines = [
        "# GeoChange Lab Analysis Report",
        "",
        "## Executive summary",
        "",
        f"- **{len(result.regions)}** material change region(s) detected.",
        f"- **{result.changed_ratio:.2%}** of image pixels were classified as changed.",
        f"- Registration offset: **dx={result.alignment.dx}, dy={result.alignment.dy}** pixels.",
        f"- Alignment reduced normalized image error by **{max(alignment_gain, 0):.2%}**.",
        f"- Adaptive decision threshold: **{result.threshold:.3f}**.",
        "",
        "## Detected regions",
        "",
        "| Region | Severity | Area (px) | Bounding box | Mean score |",
        "|---:|:---:|---:|:---|---:|",
    ]
    for region in result.regions:
        lines.append(
            f"| {region.id} | {region.severity} | {region.area_pixels} | "
            f"`{region.bbox}` | {region.mean_score:.3f} |"
        )
    if not result.regions:
        lines.append("| — | none | 0 | — | — |")
    lines.extend(
        [
            "",
            "## Interpretation notes",
            "",
            "This is a screening tool, not an authoritative land-use decision system. "
            "Clouds, seasonal vegetation, shadows, sensor differences, and imperfect "
            "registration can create false positives. A human reviewer should inspect "
            "each highlighted region and compare it with source metadata.",
        ]
    )
    return "\n".join(lines) + "\n"

