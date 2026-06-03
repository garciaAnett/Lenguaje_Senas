"""
Router: /dataset
Gestión del dataset de clips de video – Sprint 2.
Endpoints: upload, listado, estadísticas y recalcular split.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from schemas.dataset import (
    DatasetEntry, DatasetListResponse, DatasetStatsResponse,
    SplitStats, ClassStats, UploadResponse,
)
from utils.dataset_utils import (
    load_dataset_index, save_clip, compute_split, get_stats,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset", tags=["Dataset"])

ALLOWED_TYPES = {"video/mp4", "video/webm", "video/ogg", "application/octet-stream"}
MAX_SIZE_MB = 50

# Distribución de palabras por participante (Sprint 2)
PALABRAS_RODRIGO = ["Hola", "Gracias", "Sí", "No", "Ayuda", "Agua", "Comida"]
PALABRAS_ANETT   = ["Baño", "Casa", "Escuela", "Amigo", "Familia", "Perdón", "Por favor", "Adiós"]


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir clip de video etiquetado",
    description=(
        "Recibe un clip WebM o MP4 (2-3 s), lo guarda en `dataset/raw/<palabra>/` "
        "y actualiza el `dataset_index.csv`. El split se asigna automáticamente (70/15/15)."
    ),
)
async def upload_clip(
    video: Annotated[UploadFile, File(description="Clip WebM/MP4 de la seña (2-3 s, 15-30 fps)")],
    palabra: Annotated[str, Form(description="Palabra del MVP que representa el clip")],
    participante: Annotated[str, Form(description="Nombre del grabador: 'rodrigo' o 'anett'")],
    duracion: Annotated[float, Form(description="Duración del clip en segundos")] = 2.5,
    fps: Annotated[int, Form(description="FPS del clip")] = 30,
):
    if video.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo no soportado: {video.content_type}. Usa MP4 o WebM.",
        )

    video_bytes = await video.read()

    if len(video_bytes) == 0:
        raise HTTPException(status_code=400, detail="Archivo de video vacío.")
    if len(video_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"El archivo supera {MAX_SIZE_MB} MB.")

    entry_dict = await save_clip(
        video_bytes=video_bytes,
        palabra=palabra,
        participante=participante,
        duracion=duracion,
        fps=fps,
        original_filename=video.filename or "clip.webm",
    )

    logger.info(f"[/dataset/upload] {entry_dict['sample_id']} | {entry_dict['palabra']} | split={entry_dict['split']}")

    return UploadResponse(
        message="Clip guardado correctamente",
        entry=DatasetEntry(**entry_dict),
    )


@router.get(
    "",
    response_model=DatasetListResponse,
    summary="Listar entradas del dataset",
    description="Devuelve todas las entradas del CSV. Acepta filtros opcionales.",
)
async def list_dataset(
    palabra: str | None = None,
    split: str | None = None,
    participante: str | None = None,
):
    rows = load_dataset_index()

    if palabra:
        rows = [r for r in rows if r["palabra"].lower() == palabra.lower()]
    if split:
        rows = [r for r in rows if r["split"] == split]
    if participante:
        rows = [r for r in rows if r["participante"].lower() == participante.lower()]

    entries = [DatasetEntry(**r) for r in rows]
    return DatasetListResponse(total=len(entries), entries=entries)


@router.get(
    "/stats",
    response_model=DatasetStatsResponse,
    summary="Estadísticas del dataset",
    description="Total de clips, palabras cubiertas, distribución por split y por clase.",
)
async def dataset_stats():
    stats = get_stats()
    return DatasetStatsResponse(
        total_clips=stats["total_clips"],
        palabras_cubiertas=stats["palabras_cubiertas"],
        splits=SplitStats(**stats["splits"]),
        por_clase=[ClassStats(**c) for c in stats["por_clase"]],
        palabras_pendientes=stats["palabras_pendientes"],
    )


@router.post(
    "/split",
    summary="Recalcular split train/val/test",
    description="Redistribuye aleatoriamente las muestras: 70% train, 15% val, 15% test por clase.",
)
async def recalculate_split():
    result = compute_split()
    return {"message": "Split recalculado", **result}


@router.get(
    "/palabras",
    summary="Palabras por participante",
    description="Lista qué palabras graba cada participante en Sprint 2.",
)
async def palabras_por_participante():
    return {
        "rodrigo": {"palabras": PALABRAS_RODRIGO, "total": len(PALABRAS_RODRIGO)},
        "anett":   {"palabras": PALABRAS_ANETT,   "total": len(PALABRAS_ANETT)},
    }
