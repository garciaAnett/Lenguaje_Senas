"""
Router: /dataset
Sprint 2 — guardado de clips para construir el dataset de entrenamiento.
Guarda en backend/dataset/clips/{palabra}/clip_001.webm
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

logger = logging.getLogger(__name__)
router = APIRouter()

CLIPS_DIR = Path(__file__).parent.parent / "dataset" / "clips"
INDEX_CSV = Path(__file__).parent.parent / "dataset" / "dataset_index.csv"


def _next_filename(palabra: str) -> tuple[int, Path]:
    word_dir = CLIPS_DIR / palabra
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


@router.post("/dataset/upload", status_code=status.HTTP_201_CREATED)
async def upload_clip(
    video: UploadFile = File(...),
    palabra: str = Form(...),
    participante: str = Form(default="anett"),
    duracion: float = Form(default=3.0),
    fps: int = Form(default=30),
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
    archivo_rel = f"dataset/clips/{palabra}/clip_{n:03d}.webm"
    _append_csv(palabra, archivo_rel, len(video_bytes))

    logger.info(f"[dataset] {ruta.name} guardado para '{palabra}' ({len(video_bytes)} bytes)")
    return {
        "ok": True,
        "clip_numero": n,
        "palabra": palabra,
        "archivo": ruta.name,
        "total_clips_palabra": n,
    }


@router.get("/dataset/stats")
async def dataset_stats():
    stats: dict[str, int] = {}
    if CLIPS_DIR.exists():
        for word_dir in sorted(CLIPS_DIR.iterdir()):
            if word_dir.is_dir():
                count = len(list(word_dir.glob("clip_*.webm")))
                if count > 0:
                    stats[word_dir.name] = count
    return {"total": sum(stats.values()), "por_palabra": stats}
