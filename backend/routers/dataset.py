"""
Router: /dataset
Sprint 2 — guardado de clips para construir el dataset de entrenamiento.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.model_manager import PALABRAS_MVP

logger = logging.getLogger(__name__)
router = APIRouter()

DATASET_DIR = Path(__file__).parent.parent / "dataset" / "clips"
INDEX_CSV   = Path(__file__).parent.parent / "dataset" / "dataset_index.csv"
PALABRAS_VALIDAS = {p["palabra"] for p in PALABRAS_MVP}


def _next_filename(palabra: str) -> tuple[int, Path]:
    word_dir = DATASET_DIR / palabra
    word_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(word_dir.glob("clip_*.webm"))) + 1
    return n, word_dir / f"clip_{n:03d}.webm"


def _append_csv(palabra: str, archivo: str, size_bytes: int):
    INDEX_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_header = not INDEX_CSV.exists()
    with open(INDEX_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["clip_id", "palabra", "archivo", "fecha", "size_bytes", "grabado_por"])
        clip_id = f"{palabra}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        writer.writerow([clip_id, palabra, archivo, datetime.now().isoformat(), size_bytes, "Anett"])


@router.post(
    "/dataset/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Guardar clip de seña para el dataset",
)
async def upload_clip(
    video: UploadFile = File(..., description="Clip .webm de 2-5 segundos"),
    palabra: str = Form(..., description="Palabra que se está haciendo la seña"),
):
    palabra = palabra.strip()
    if not palabra:
        raise HTTPException(status_code=400, detail="El campo 'palabra' no puede estar vacío.")

    video_bytes = await video.read()
    if not video_bytes:
        raise HTTPException(status_code=400, detail="El clip está vacío.")
    if len(video_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="El clip supera 50 MB.")

    n, ruta = _next_filename(palabra)
    ruta.write_bytes(video_bytes)
    archivo_rel = str(ruta.relative_to(Path(__file__).parent.parent))
    _append_csv(palabra, archivo_rel, len(video_bytes))

    logger.info(f"[dataset] {ruta.name} guardado para '{palabra}' ({len(video_bytes)} bytes)")
    return {
        "ok": True,
        "clip_numero": n,
        "palabra": palabra,
        "archivo": ruta.name,
        "total_clips_palabra": n,
    }


@router.get("/dataset/stats", summary="Conteo de clips por palabra")
async def dataset_stats():
    stats: dict[str, int] = {p["palabra"]: 0 for p in PALABRAS_MVP}
    if DATASET_DIR.exists():
        for palabra in stats:
            d = DATASET_DIR / palabra
            if d.exists():
                stats[palabra] = len(list(d.glob("clip_*.webm")))
    return {"total": sum(stats.values()), "por_palabra": stats}
