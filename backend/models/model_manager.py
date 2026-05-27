"""
ModelManager – gestiona el ciclo de vida del modelo VideoMAE.

Sprint 1: modo MOCK (sin modelo real).
Sprint 3: se reemplaza load() para cargar el fine-tuned desde Hugging Face.
"""

import os
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 15 palabras del MVP con su class_id
PALABRAS_MVP = [
    {"class_id": 0,  "palabra": "Hola"},
    {"class_id": 1,  "palabra": "Gracias"},
    {"class_id": 2,  "palabra": "Sí"},
    {"class_id": 3,  "palabra": "No"},
    {"class_id": 4,  "palabra": "Ayuda"},
    {"class_id": 5,  "palabra": "Agua"},
    {"class_id": 6,  "palabra": "Comida"},
    {"class_id": 7,  "palabra": "Baño"},
    {"class_id": 8,  "palabra": "Casa"},
    {"class_id": 9,  "palabra": "Escuela"},
    {"class_id": 10, "palabra": "Amigo"},
    {"class_id": 11, "palabra": "Familia"},
    {"class_id": 12, "palabra": "Perdón"},
    {"class_id": 13, "palabra": "Por favor"},
    {"class_id": 14, "palabra": "Adiós"},
]

# HF config – se usa desde Sprint 3
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "")          # ej. "villarroel/videomae-sign-language"
HF_TOKEN    = os.getenv("HUGGINGFACE_TOKEN", "")


class ModelManager:
    """
    Encapsula carga, inferencia y estado del modelo.
    En modo mock devuelve predicciones aleatorias realistas.
    """

    def __init__(self):
        self.model    = None
        self.pipeline = None
        self.loaded   = False
        self.mock_mode = True   # False en Sprint 3

    # ──────────────────────────────────────────
    # Carga
    # ──────────────────────────────────────────
    async def load(self):
        """
        Sprint 1 → mock (no carga nada).
        Sprint 3 → descomentar bloque HF.
        """
        if self.mock_mode:
            logger.info("ModelManager: modo MOCK activo (Sprint 1).")
            self.loaded = False
            return

        # ── SPRINT 3: descomentar cuando el fine-tuning esté listo ──────────
        # from transformers import pipeline as hf_pipeline
        # logger.info(f"Cargando modelo desde HF: {HF_MODEL_ID}")
        # self.pipeline = hf_pipeline(
        #     "video-classification",
        #     model=HF_MODEL_ID,
        #     token=HF_TOKEN or None,
        # )
        # self.loaded = True
        # logger.info("Modelo cargado correctamente.")
        # ────────────────────────────────────────────────────────────────────

    # ──────────────────────────────────────────
    # Inferencia
    # ──────────────────────────────────────────
    def predict_mock(self, n_frames: int = 0) -> dict:
        """
        Predicción mock: clase aleatoria con confianza realista.
        Simula la respuesta que dará VideoMAE en Sprint 3.
        """
        # Elige clase ganadora al azar
        ganadora = random.choice(PALABRAS_MVP)

        # Genera probabilidades: una alta para la ganadora, resto reparten el residuo
        prob_ganadora = round(random.uniform(0.70, 0.97), 4)
        residuo = round(1.0 - prob_ganadora, 4)

        otras = [p for p in PALABRAS_MVP if p["class_id"] != ganadora["class_id"]]
        random.shuffle(otras)

        # Top-3
        prob2 = round(random.uniform(0, residuo * 0.7), 4)
        prob3 = round(residuo - prob2, 4)

        top3 = [
            {"palabra": ganadora["palabra"],  "class_id": ganadora["class_id"],  "confianza": prob_ganadora},
            {"palabra": otras[0]["palabra"],  "class_id": otras[0]["class_id"],  "confianza": prob2},
            {"palabra": otras[1]["palabra"],  "class_id": otras[1]["class_id"],  "confianza": prob3},
        ]

        return {
            "prediccion": top3[0],
            "top3": top3,
            "modo": "mock",
            "modelo": "N/A (Sprint 1)",
            "frames_recibidos": n_frames,
        }

    async def predict_real(self, frames) -> dict:
        """
        Sprint 3: inferencia real con VideoMAE.
        Se implementa cuando self.loaded is True.
        """
        if not self.loaded or self.pipeline is None:
            raise RuntimeError("Modelo no cargado. Usa predict_mock() en Sprint 1.")

        # TODO Sprint 3: preprocesar frames y llamar self.pipeline
        raise NotImplementedError("predict_real se implementa en Sprint 3.")

    # ──────────────────────────────────────────
    # Info
    # ──────────────────────────────────────────
    @property
    def modo(self) -> str:
        return "mock" if self.mock_mode else "real"

    @staticmethod
    def palabras() -> list[str]:
        return [p["palabra"] for p in PALABRAS_MVP]
