from __future__ import annotations

from typing import Iterable

from .models import AnalysisResult


def _project(x: float, y: float, width: int, height: int, bounds):
    if bounds is None:
        return [round(x, 2), round(y, 2)]
    west, south, east, north = bounds
    longitude = west + (x / width) * (east - west)
    latitude = north - (y / height) * (north - south)
    return [round(longitude, 7), round(latitude, 7)]


def to_geojson(result: AnalysisResult, bounds: Iterable[float] | None = None) -> dict:
    normalized_bounds = tuple(bounds) if bounds is not None else None
    if normalized_bounds is not None and len(normalized_bounds) != 4:
        raise ValueError("bounds must contain west, south, east, north")
    features = []
    for region in result.regions:
        x0, y0, x1, y1 = region.bbox
        ring = [
            _project(x0, y0, result.width, result.height, normalized_bounds),
            _project(x1, y0, result.width, result.height, normalized_bounds),
            _project(x1, y1, result.width, result.height, normalized_bounds),
            _project(x0, y1, result.width, result.height, normalized_bounds),
            _project(x0, y0, result.width, result.height, normalized_bounds),
        ]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [ring]},
                "properties": {
                    "id": region.id,
                    "severity": region.severity,
                    "area_pixels": region.area_pixels,
                    "mean_score": region.mean_score,
                    "coordinate_space": "WGS84" if normalized_bounds else "pixel",
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}

