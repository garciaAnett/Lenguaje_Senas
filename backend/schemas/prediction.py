"""
Schemas Pydantic para los endpoints de predicción y health.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ──────────────────────────────────────────────
# Palabras MVP (15 palabras definidas en el plan)
# ──────────────────────────────────────────────
class PalabraMVP(str, Enum):
    HOLA       = "Hola"
    GRACIAS    = "Gracias"
    SI         = "Sí"
    NO         = "No"
    AYUDA      = "Ayuda"
    AGUA       = "Agua"
    COMIDA     = "Comida"
    BANO       = "Baño"
    CASA       = "Casa"
    ESCUELA    = "Escuela"
    AMIGO      = "Amigo"
    FAMILIA    = "Familia"
    PERDON     = "Perdón"
    POR_FAVOR  = "Por favor"
    ADIOS      = "Adiós"


# ──────────────────────────────────────────────
# Response: predicción individual
# ──────────────────────────────────────────────
class PredictionItem(BaseModel):
    palabra: str = Field(..., description="Palabra reconocida")
    class_id: int = Field(..., description="ID de clase (0-14)")
    confianza: float = Field(..., ge=0.0, le=1.0, description="Confianza del modelo (0-1)")

    model_config = {"json_schema_extra": {"example": {"palabra": "Hola", "class_id": 0, "confianza": 0.95}}}


class PredictResponse(BaseModel):
    prediccion: PredictionItem
    top3: list[PredictionItem] = Field(default_factory=list, description="Top 3 predicciones")
    modo: str = Field(default="mock", description="'mock' en Sprint 1, 'real' desde Sprint 3")
    modelo: str = Field(default="N/A", description="Nombre del modelo cargado")
    frames_recibidos: int = Field(default=0, description="Cantidad de frames analizados")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prediccion": {"palabra": "Hola", "class_id": 0, "confianza": 0.91},
                "top3": [
                    {"palabra": "Hola",    "class_id": 0, "confianza": 0.91},
                    {"palabra": "Adiós",   "class_id": 14, "confianza": 0.06},
                    {"palabra": "Gracias", "class_id": 1, "confianza": 0.03},
                ],
                "modo": "mock",
                "modelo": "N/A",
                "frames_recibidos": 48,
            }
        }
    }


# ──────────────────────────────────────────────
# Response: health
# ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = Field(..., description="'ok' si el servidor está activo")
    modelo_cargado: bool = Field(..., description="True si el modelo VideoMAE está en memoria")
    modo: str = Field(..., description="'mock' o 'real'")
    palabras_soportadas: list[str] = Field(..., description="Lista de las 15 palabras del MVP")
    version: str = Field(default="0.1.0")
    sprint: int = Field(default=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "modelo_cargado": False,
                "modo": "mock",
                "palabras_soportadas": ["Hola", "Gracias", "Sí", "No", "Ayuda"],
                "version": "0.1.0",
                "sprint": 1,
            }
        }
    }
