"""
Router: /health
Verifica que el servidor está activo y reporta el estado del modelo.
"""

from fastapi import APIRouter, Request
from schemas.prediction import HealthResponse
from models.model_manager import ModelManager

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Estado del servidor y del modelo",
    description=(
        "Devuelve el estado del servidor. "
        "En Sprint 1 el campo `modelo_cargado` siempre es `false` (modo mock). "
        "En Sprint 3 pasa a `true` cuando VideoMAE está en memoria."
    ),
)
async def health(request: Request):
    manager: ModelManager = request.app.state.model_manager

    return HealthResponse(
        status="ok",
        modelo_cargado=manager.loaded,
        modo=manager.modo,
        palabras_soportadas=manager.palabras(),
        version="0.1.0",
        sprint=1,
    )
