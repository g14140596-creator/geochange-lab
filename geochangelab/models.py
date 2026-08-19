from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Alignment:
    dx: int
    dy: int
    mae_before: float
    mae_after: float


@dataclass(frozen=True)
class ChangeRegion:
    id: int
    area_pixels: int
    bbox: tuple[int, int, int, int]
    centroid: tuple[float, float]
    mean_score: float
    max_score: float
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisResult:
    width: int
    height: int
    threshold: float
    changed_pixels: int
    changed_ratio: float
    alignment: Alignment
    regions: tuple[ChangeRegion, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["regions"] = [region.to_dict() for region in self.regions]
        return data

