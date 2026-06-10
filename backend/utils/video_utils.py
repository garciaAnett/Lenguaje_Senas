"""
Utilidades de video - Sprint 3: extracción real de frames con PyAV.
"""

import logging
import os
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

NUM_FRAMES = 16  # VideoMAE estándar


def extract_frames_from_bytes(video_bytes: bytes, num_frames: int = NUM_FRAMES) -> list:
    """
    Extrae num_frames uniformemente distribuidos del clip (en bytes).
    Usa PyAV. Devuelve lista de arrays numpy RGB (H, W, 3).
    """
    try:
        import av
    except ImportError:
        logger.warning("PyAV no instalado; devolviendo frames negros de placeholder.")
        return [np.zeros((224, 224, 3), dtype=np.uint8) for _ in range(num_frames)]

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        return _decode_and_sample(tmp_path, num_frames)
    except Exception as e:
        logger.warning(f"extract_frames_from_bytes error: {e}")
        return [np.zeros((224, 224, 3), dtype=np.uint8) for _ in range(num_frames)]
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def extract_frames_from_path(video_path: "str | Path", num_frames: int = NUM_FRAMES) -> list:
    """Versión path-based, usada en el training script."""
    try:
        import av  # noqa: F401
    except ImportError:
        return [np.zeros((224, 224, 3), dtype=np.uint8) for _ in range(num_frames)]

    try:
        return _decode_and_sample(str(video_path), num_frames)
    except Exception as e:
        logger.warning(f"extract_frames_from_path error ({video_path}): {e}")
        return [np.zeros((224, 224, 3), dtype=np.uint8) for _ in range(num_frames)]


def _decode_and_sample(path: str, num_frames: int) -> list:
    import av

    frames = []
    container = av.open(path)
    for frame in container.decode(video=0):
        frames.append(frame.to_ndarray(format="rgb24"))
    container.close()

    if not frames:
        return [np.zeros((224, 224, 3), dtype=np.uint8) for _ in range(num_frames)]

    indices = np.linspace(0, len(frames) - 1, num_frames, dtype=int)
    return [frames[i] for i in indices]


def count_frames_from_bytes(video_bytes: bytes) -> int:
    """Cuenta frames de un clip dado en bytes. Usa PyAV o estimación heurística."""
    try:
        frames = extract_frames_from_bytes(video_bytes, num_frames=9999)
        return len(frames)
    except Exception:
        return len(video_bytes) // 5000
