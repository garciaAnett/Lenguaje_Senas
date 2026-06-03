"""
Utilidades de video para preprocesamiento de clips.

Sprint 1: solo count_frames_from_bytes (sin dependencia de OpenCV).
Sprint 2/3: se añaden extract_frames(), resize_frames(), normalize_frames().
"""

import io
import logging
import struct
from typing import Optional

logger = logging.getLogger(__name__)


def count_frames_from_bytes(video_bytes: bytes) -> int:
    """
    Estima el número de frames de un video a partir de sus bytes.
    Sprint 1: lectura básica sin OpenCV; devuelve 0 si no puede parsear.
    Sprint 3: reemplazar con extracción real via OpenCV/PyAV.
    """
    try:
        # Intento rápido: si OpenCV está instalado, usarlo
        import cv2
        import numpy as np

        arr = np.frombuffer(video_bytes, dtype=np.uint8)
        cap = cv2.VideoCapture()
        # En memoria con imdecode no aplica; necesitamos un archivo temporal
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        cap = cv2.VideoCapture(tmp_path)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        os.unlink(tmp_path)
        return max(n, 0)
    except ImportError:
        logger.debug("OpenCV no instalado; count_frames devuelve estimación por tamaño.")
        # Estimación heurística: ~150 KB por segundo a 30fps → ~5 KB/frame
        estimated = len(video_bytes) // 5000
        return max(estimated, 0)
    except Exception as e:
        logger.warning(f"count_frames_from_bytes error: {e}")
        return 0


# ── Sprint 3: descomentar cuando OpenCV esté disponible ──────────────────────
# import cv2
# import numpy as np
#
# def extract_frames(video_bytes: bytes, target_frames: int = 16) -> list:
#     """
#     Extrae `target_frames` uniformemente distribuidos del clip.
#     Devuelve lista de arrays numpy (H, W, C).
#     """
#     import tempfile, os
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
#         tmp.write(video_bytes)
#         tmp_path = tmp.name
#
#     cap = cv2.VideoCapture(tmp_path)
#     total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     indices = np.linspace(0, total - 1, target_frames, dtype=int)
#
#     frames = []
#     for idx in indices:
#         cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
#         ret, frame = cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             frames.append(frame)
#
#     cap.release()
#     os.unlink(tmp_path)
#     return frames
#
#
# def resize_frames(frames: list, size: tuple = (224, 224)) -> list:
#     return [cv2.resize(f, size) for f in frames]
#
#
# def normalize_frames(frames: list) -> np.ndarray:
#     """Normaliza a [0,1] y devuelve shape (T, H, W, C)."""
#     arr = np.stack(frames).astype(np.float32) / 255.0
#     return arr
# ─────────────────────────────────────────────────────────────────────────────
