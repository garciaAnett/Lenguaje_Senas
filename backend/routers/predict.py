"""
Router: /predict
Recibe un clip de video y devuelve la predicción del modelo VideoMAE.

Sprint 1/2 → modo mock.
Sprint 3   → inferencia real con modelo fine-tuned.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from models.model_manager import ModelManager, PALABRAS_MVP
from schemas.prediction import PredictResponse
from utils.video_utils import count_frames_from_bytes

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_TYPES = {"video/mp4", "video/webm", "video/ogg", "application/octet-stream"}
MAX_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Clasificar clip de lenguaje de señas",
    description=(
        "Recibe un clip de video corto (2–3 s) capturado desde la cámara web "
        "y devuelve la palabra reconocida con su confianza. "
        "**Sprint 3:** inferencia real con VideoMAE fine-tuned cuando APP_MODE=real."
    ),
)
async def predict(
    request: Request,
    video: Annotated[
        UploadFile,
        File(description="Clip de video MP4/WebM de la seña (2–3 segundos, 15–30 fps)"),
    ],
):
    manager: ModelManager = request.app.state.model_manager

    if video.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo no soportado: {video.content_type}. Usa MP4 o WebM.",
        )

    video_bytes = await video.read()

    if len(video_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo vacío.")

    if len(video_bytes) > MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Archivo supera 50 MB.")

    n_frames = count_frames_from_bytes(video_bytes)
    logger.info(
        "[/predict] %r | %d bytes | frames≈%d | modo=%s",
        video.filename, len(video_bytes), n_frames, manager.modo,
    )

    if manager.mock_mode:
        result = manager.predict_mock(n_frames=n_frames)
    else:
        try:
            result = await manager.predict_real(video_bytes=video_bytes)
        except Exception:
            logger.exception("predict_real falló; usando mock como fallback.")
            result = manager.predict_mock(n_frames=n_frames)

    return PredictResponse(**result)


@router.get(
    "/predict/palabras",
    summary="Listar palabras soportadas",
    description="Devuelve las 15 palabras del MVP con su class_id.",
)
async def listar_palabras():
    return {"total": len(PALABRAS_MVP), "palabras": PALABRAS_MVP}
