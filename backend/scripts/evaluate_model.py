"""
Evaluación del modelo VideoMAE fine-tuned con métricas detalladas.
Sprint 3 - Rodrigo Villarroel  |  10/06/2026

Genera:
  - Accuracy top-1 y top-3
  - Precision, Recall, F1 por clase
  - Matriz de confusión
  - Tiempo de inferencia promedio
  - dataset/metrics/eval_metrics.json

Uso:
  cd backend
  python scripts/evaluate_model.py
  python scripts/evaluate_model.py --model-path models/checkpoints/videomae-sign-language/best
  python scripts/evaluate_model.py --model-path villarroel/videomae-sign-language-mvp  # desde HF Hub
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).parent.parent
CLIPS_DIR   = BACKEND_DIR / "dataset" / "clips"
METRICS_DIR = BACKEND_DIR.parent / "dataset" / "metrics"

sys.path.insert(0, str(BACKEND_DIR))

from scripts.train_videomae import (
    PALABRAS_MVP, FOLDER_ALIAS, LABEL2ID, ID2LABEL, NUM_FRAMES, _extract_frames
)

DEFAULT_MODEL = str(BACKEND_DIR / "models" / "checkpoints" / "videomae-sign-language" / "best")


def evaluate(model_path: str, hf_token: str = ""):
    from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor

    logger.info("=" * 55)
    logger.info("Evaluación del modelo VideoMAE")
    logger.info("  Modelo : %s", model_path)

    # ── Cargar modelo ──────────────────────────────────────────────
    logger.info("Cargando modelo...")
    processor = VideoMAEImageProcessor.from_pretrained(model_path, token=hf_token or None)
    model     = VideoMAEForVideoClassification.from_pretrained(model_path, token=hf_token or None)
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    logger.info("  Dispositivo: %s", device.upper())

    # ── Cargar muestras de test ───────────────────────────────────
    all_samples: list[tuple[Path, int]] = []
    for folder in sorted(CLIPS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        canonical = FOLDER_ALIAS.get(folder.name, folder.name)
        if canonical not in LABEL2ID:
            continue
        label = LABEL2ID[canonical]
        clips = sorted(folder.glob("*.webm"))
        n     = len(clips)
        if n == 0:
            continue
        # Usar las últimas ~15% como test (igual que en train)
        n_train = max(1, round(n * 0.70))
        n_val   = max(1, round(n * 0.15))
        test_clips = clips[n_train + n_val:]
        for clip in test_clips:
            all_samples.append((clip, label))

    if not all_samples:
        logger.warning("No hay clips de test. Usando todas las muestras para evaluación.")
        for folder in sorted(CLIPS_DIR.iterdir()):
            if not folder.is_dir():
                continue
            canonical = FOLDER_ALIAS.get(folder.name, folder.name)
            if canonical not in LABEL2ID:
                continue
            label = LABEL2ID[canonical]
            for clip in sorted(folder.glob("*.webm")):
                all_samples.append((clip, label))

    logger.info("  Muestras a evaluar: %d", len(all_samples))
    logger.info("=" * 55)

    # ── Inferencia ────────────────────────────────────────────────
    y_true, y_pred_top1, y_pred_top3 = [], [], []
    latencies = []

    for i, (clip_path, label) in enumerate(all_samples):
        frames = _extract_frames(clip_path)
        inputs = processor(frames, return_tensors="pt").to(device)

        t0 = time.perf_counter()
        with torch.no_grad():
            outputs = model(**inputs)
        latencies.append(time.perf_counter() - t0)

        probs   = torch.softmax(outputs.logits, dim=-1).squeeze()
        top1    = int(probs.argmax().item())
        top3    = [int(x) for x in probs.topk(3).indices.tolist()]

        y_true.append(label)
        y_pred_top1.append(top1)
        y_pred_top3.append(top3)

        if (i + 1) % 10 == 0:
            logger.info("  Procesadas %d/%d muestras...", i + 1, len(all_samples))

    # ── Métricas globales ─────────────────────────────────────────
    correct_top1 = sum(t == p for t, p in zip(y_true, y_pred_top1))
    correct_top3 = sum(t in p for t, p in zip(y_true, y_pred_top3))
    acc_top1 = correct_top1 / len(y_true)
    acc_top3 = correct_top3 / len(y_true)
    avg_lat  = np.mean(latencies) * 1000  # ms

    logger.info("Accuracy Top-1 : %.4f  (%d/%d)", acc_top1, correct_top1, len(y_true))
    logger.info("Accuracy Top-3 : %.4f  (%d/%d)", acc_top3, correct_top3, len(y_true))
    logger.info("Latencia media : %.1f ms/clip", avg_lat)

    # ── Métricas por clase ─────────────────────────────────────────
    per_class = []
    for class_id, palabra in ID2LABEL.items():
        tp = sum(1 for t, p in zip(y_true, y_pred_top1) if t == class_id and p == class_id)
        fp = sum(1 for t, p in zip(y_true, y_pred_top1) if t != class_id and p == class_id)
        fn = sum(1 for t, p in zip(y_true, y_pred_top1) if t == class_id and p != class_id)
        support = sum(1 for t in y_true if t == class_id)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class.append({
            "class_id": class_id,
            "palabra": palabra,
            "support": support,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })

    # ── Matriz de confusión ────────────────────────────────────────
    n = len(PALABRAS_MVP)
    conf_matrix = [[0] * n for _ in range(n)]
    for t, p in zip(y_true, y_pred_top1):
        conf_matrix[t][p] += 1

    # ── Guardar resultados ─────────────────────────────────────────
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "model": model_path,
        "total_samples": len(y_true),
        "accuracy_top1": round(acc_top1, 4),
        "accuracy_top3": round(acc_top3, 4),
        "avg_latency_ms": round(avg_lat, 2),
        "per_class": per_class,
        "confusion_matrix": conf_matrix,
        "labels": PALABRAS_MVP,
    }

    metrics_path = METRICS_DIR / "eval_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("Métricas guardadas: %s", metrics_path)

    # ── Reporte por clase ──────────────────────────────────────────
    logger.info("%-14s  %7s  %7s  %7s  %7s", "Palabra", "Support", "Prec", "Recall", "F1")
    logger.info("-" * 55)
    for pc in per_class:
        logger.info(
            "%-14s  %7d  %7.4f  %7.4f  %7.4f",
            pc["palabra"], pc["support"], pc["precision"], pc["recall"], pc["f1"],
        )

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluación VideoMAE – Sprint 3")
    parser.add_argument(
        "--model-path",
        default=DEFAULT_MODEL,
        help="Ruta al checkpoint local o ID del modelo en HF Hub",
    )
    parser.add_argument(
        "--hf-token",
        default=os.getenv("HUGGINGFACE_TOKEN", ""),
        help="Token de HF Hub (si el modelo es privado)",
    )
    args = parser.parse_args()
    evaluate(model_path=args.model_path, hf_token=args.hf_token)
