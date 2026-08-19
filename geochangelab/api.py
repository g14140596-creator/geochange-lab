from __future__ import annotations

import base64
import io

from PIL import Image

from .geo import to_geojson
from .pipeline import AnalysisConfig, analyze_images

try:
    from fastapi import FastAPI, File, Form, HTTPException, UploadFile
    from fastapi.responses import FileResponse
except ImportError as exc:  # pragma: no cover - optional API dependency
    raise RuntimeError("Install GeoChange Lab with the 'api' extra") from exc


app = FastAPI(title="GeoChange Lab API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def home():
    return FileResponse("web/index.html")


@app.post("/api/analyze")
async def analyze(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    sensitivity: float = Form(3.5),
    min_area: int = Form(24),
):
    try:
        before_image = Image.open(io.BytesIO(await before.read())).convert("RGB")
        after_image = Image.open(io.BytesIO(await after.read())).convert("RGB")
        result, overlay, _, _ = analyze_images(
            before_image,
            after_image,
            AnalysisConfig(sensitivity=sensitivity, min_area=min_area),
        )
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    output = io.BytesIO()
    Image.fromarray(overlay).save(output, format="PNG")
    return {
        "analysis": result.to_dict(),
        "geojson": to_geojson(result),
        "overlay_png_base64": base64.b64encode(output.getvalue()).decode("ascii"),
    }

