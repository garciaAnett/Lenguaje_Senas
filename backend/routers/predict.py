"""
Router: /predict
Recibe un clip de video (como archivo o como frames base64) y devuelve la predicción.

Sprint 1 → modo mock: ignora el contenido real del video y devuelve clase aleatoria.
Sprint 3 → modo real: procesa frames con VideoMAE.
"""

import io
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from models.model_manager import ModelManager
from schemas.prediction import PredictResponse
from utils.video_utils import count_frames_from_bytes

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────────────────────────
# POST /predict  – recibe un clip de video
# ──────────────────────────────────────────────────────────────────
@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Clasificar clip de lenguaje de señas",
    description=(
        "Recibe un clip de video corto (2–3 s) capturado desde la cámara web "
        "y devuelve la palabra reconocida con su confianza. "
        "**Sprint 1:** respuesta mock (aleatoria). "
        "**Sprint 3:** inferencia real con VideoMAE fine-tuned."
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

    # ── Validación básica del archivo ──────────────────────────────
    allowed_types = {"video/mp4", "video/webm", "video/ogg", "application/octet-stream"}
    if video.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {video.content_type}. Usa MP4 o WebM.",
        )

    video_bytes = await video.read()
    if len(video_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo de video está vacío.",
        )

    # Límite 50 MB (clips cortos no deberían superar esto)
    if len(video_bytes) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 50 MB.",
        )

    # ── Conteo de frames (best-effort) ────────────────────────────
    n_frames = count_frames_from_bytes(video_bytes)
    logger.info(
        f"[/predict] archivo recibido: {video.filename!r} | "
        f"size={len(video_bytes)} bytes | frames≈{n_frames} | modo={manager.modo}"
    )

    # ── Predicción ────────────────────────────────────────────────
    if manager.mock_mode:
        result = manager.predict_mock(n_frames=n_frames)
    else:
        # Sprint 3: aquí se envían los frames reales a VideoMAE
        try:
            result = await manager.predict_real(frames=video_bytes)
        except NotImplementedError:
            # Fallback a mock si el modelo real todavía no está listo
            logger.warning("predict_real no implementado, usando mock como fallback.")
            result = manager.predict_mock(n_frames=n_frames)

    return PredictResponse(**result)


# ──────────────────────────────────────────────────────────────────
# GET /predict/palabras  – lista las 15 palabras soportadas
# ──────────────────────────────────────────────────────────────────
@router.get(
    "/predict/palabras",
    summary="Listar palabras soportadas",
    description="Devuelve las 15 palabras del MVP con su class_id.",
)
async def listar_palabras():
    from models.model_manager import PALABRAS_MVP
    return {"total": len(PALABRAS_MVP), "palabras": PALABRAS_MVP}
