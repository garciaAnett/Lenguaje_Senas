"""
Schemas Pydantic para gestión del dataset de señas.
Sprint 2: upload, listado, estadísticas y split.
"""

from pydantic import BaseModel, Field


class DatasetEntry(BaseModel):
    sample_id: str = Field(..., description="ID único del clip (ej. R001)")
    palabra: str = Field(..., description="Palabra representada")
    class_id: int = Field(..., description="ID de clase (0-14)")
    participante: str = Field(..., description="Nombre del grabador")
    video_path: str = Field(..., description="Ruta relativa al clip")
    duracion: float = Field(..., description="Duración en segundos")
    fps: int = Field(..., description="Frames por segundo")
    split: str = Field(..., description="'train', 'val' o 'test'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sample_id": "R001",
                "palabra": "Hola",
                "class_id": 0,
                "participante": "rodrigo",
                "video_path": "dataset/raw/hola/R001_hola.webm",
                "duracion": 2.5,
                "fps": 30,
                "split": "train",
            }
        }
    }


class UploadResponse(BaseModel):
    message: str
    entry: DatasetEntry


class DatasetListResponse(BaseModel):
    total: int
    entries: list[DatasetEntry]


class SplitStats(BaseModel):
    train: int
    val: int
    test: int


class ClassStats(BaseModel):
    palabra: str
    class_id: int
    total: int
    train: int
    val: int
    test: int


class DatasetStatsResponse(BaseModel):
    total_clips: int
    palabras_cubiertas: int
    splits: SplitStats
    por_clase: list[ClassStats]
    palabras_pendientes: list[str]
