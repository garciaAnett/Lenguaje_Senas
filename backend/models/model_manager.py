"""
ModelManager – Sprint 3: carga y inferencia real con VideoMAE fine-tuned.

Modos de operación (variable de entorno APP_MODE):
  mock  → predicción aleatoria realista (Sprint 1/2, default)
  real  → VideoMAE desde HF Hub (HF_MODEL_ID) o checkpoint local (LOCAL_MODEL_PATH)
"""

import asyncio
import logging
import os
import random
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Vocabulario MVP ──────────────────────────────────────────────────────────
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

ID2LABEL = {p["class_id"]: p["palabra"] for p in PALABRAS_MVP}
LABEL2ID = {p["palabra"]: p["class_id"] for p in PALABRAS_MVP}

# ── Config desde entorno ─────────────────────────────────────────────────────
APP_MODE         = os.getenv("APP_MODE", "mock")          # "mock" | "real"
HF_MODEL_ID      = os.getenv("HF_MODEL_ID", "")
HF_TOKEN         = os.getenv("HUGGINGFACE_TOKEN", "")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "")      # ruta al checkpoint local


class ModelManager:
    """
    Encapsula carga, inferencia y estado del modelo VideoMAE.
    Sprint 3: modo real activo cuando APP_MODE=real.
    """

    def __init__(self):
        self.model       = None
        self.processor   = None
        self.loaded      = False
        self.mock_mode   = APP_MODE != "real"
        self._model_name = "N/A"

    # ── Carga ────────────────────────────────────────────────────────────────
    async def load(self):
        if self.mock_mode:
            logger.info("ModelManager: modo MOCK (APP_MODE=%s).", APP_MODE)
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_sync)
        except Exception:
            logger.exception("Error cargando modelo VideoMAE. Fallback a mock.")
            self.mock_mode = True

    def _load_sync(self):
        """Carga bloqueante: HF Hub o checkpoint local."""
        from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor

        source = HF_MODEL_ID or LOCAL_MODEL_PATH
        if not source:
            raise ValueError(
                "Configura HF_MODEL_ID (HF Hub) o LOCAL_MODEL_PATH (local) para APP_MODE=real."
            )

        # Resolver ruta local relativa a backend/
        if LOCAL_MODEL_PATH and not HF_MODEL_ID:
            backend_dir = Path(__file__).parent.parent
            resolved = Path(LOCAL_MODEL_PATH)
            if not resolved.is_absolute():
                resolved = backend_dir / resolved
            source = str(resolved)
            logger.info("Cargando modelo desde checkpoint local: %s", source)
        else:
            logger.info("Cargando modelo desde HF Hub: %s", source)

        self.processor = VideoMAEImageProcessor.from_pretrained(
            source, token=HF_TOKEN or None
        )
        self.model = VideoMAEForVideoClassification.from_pretrained(
            source, token=HF_TOKEN or None
        )
        self.model.eval()
        self._model_name = source
        self.loaded = True
        logger.info("Modelo VideoMAE cargado. Clases: %d", self.model.config.num_labels)

    # ── Inferencia mock ──────────────────────────────────────────────────────
    def predict_mock(self, n_frames: int = 0) -> dict:
        ganadora = random.choice(PALABRAS_MVP)
        prob_ganadora = round(random.uniform(0.70, 0.97), 4)
        residuo = round(1.0 - prob_ganadora, 4)
        otras = [p for p in PALABRAS_MVP if p["class_id"] != ganadora["class_id"]]
        random.shuffle(otras)
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
            "modelo": "N/A (mock)",
            "frames_recibidos": n_frames,
        }

    # ── Inferencia real ──────────────────────────────────────────────────────
    async def predict_real(self, video_bytes: bytes) -> dict:
        if not self.loaded:
            raise RuntimeError("Modelo no cargado. Usa predict_mock() o activa APP_MODE=real.")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._infer, video_bytes)

    def _infer(self, video_bytes: bytes) -> dict:
        import torch
        from utils.video_utils import extract_frames_from_bytes

        frames = extract_frames_from_bytes(video_bytes, num_frames=16)
        n_frames = len(frames)

        inputs = self.processor(frames, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.softmax(outputs.logits, dim=-1).squeeze().tolist()

        indexed = sorted(enumerate(probs), key=lambda x: x[1], reverse=True)
        top3 = [
            {
                "palabra": ID2LABEL.get(i, f"clase_{i}"),
                "class_id": i,
                "confianza": round(p, 4),
            }
            for i, p in indexed[:3]
        ]

        return {
            "prediccion": top3[0],
            "top3": top3,
            "modo": "real",
            "modelo": self._model_name,
            "frames_recibidos": n_frames,
        }

    # ── Info ─────────────────────────────────────────────────────────────────
    @property
    def modo(self) -> str:
        return "mock" if self.mock_mode else "real"

    @staticmethod
    def palabras() -> list[str]:
        return [p["palabra"] for p in PALABRAS_MVP]
