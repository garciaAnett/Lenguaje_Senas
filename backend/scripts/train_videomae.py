"""
Fine-tuning de VideoMAE para clasificación de lenguaje de señas.
Sprint 3 - Rodrigo Villarroel  |  10/06/2026

Dataset : backend/dataset/clips/<Palabra>/clip_XXX.webm
Base    : MCG-NJU/videomae-base  (16 frames, 224x224)
Salida  : backend/models/checkpoints/videomae-sign-language/best/

Prerrequisitos (ya en requirements.txt Sprint 3):
  transformers, torch, torchvision, av, numpy, evaluate, huggingface-hub

Uso:
  cd backend
  python scripts/train_videomae.py
  python scripts/train_videomae.py --epochs 20 --batch-size 4
  python scripts/train_videomae.py --push-hub --hf-token hf_XXX

Recomendación: usar GPU o Google Colab para reducir tiempo de entrenamiento.
  CPU estimado: ~15-30 min/epoch con este dataset.
  GPU (T4 Colab): ~2-5 min/epoch.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import numpy as np
import torch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Rutas ────────────────────────────────────────────────────────────────────
BACKEND_DIR    = Path(__file__).parent.parent
CLIPS_DIR      = BACKEND_DIR / "dataset" / "clips"
CHECKPOINT_DIR = BACKEND_DIR / "models" / "checkpoints" / "videomae-sign-language"
METRICS_DIR    = BACKEND_DIR.parent / "dataset" / "metrics"

sys.path.insert(0, str(BACKEND_DIR))

# ── Vocabulario MVP ───────────────────────────────────────────────────────────
PALABRAS_MVP = [
    "Hola", "Gracias", "Sí", "No", "Ayuda", "Agua", "Comida",
    "Baño", "Casa", "Escuela", "Amigo", "Familia", "Perdón", "Por favor", "Adiós",
]

# Alias de carpetas del dataset → clase canónica del MVP
FOLDER_ALIAS: dict[str, str] = {
    "Ayudar": "Ayuda",
}

LABEL2ID = {p: i for i, p in enumerate(PALABRAS_MVP)}
ID2LABEL = {i: p for i, p in enumerate(PALABRAS_MVP)}

# ── Defaults ─────────────────────────────────────────────────────────────────
BASE_MODEL   = "MCG-NJU/videomae-base"
NUM_FRAMES   = 16
BATCH_SIZE   = 2
EPOCHS       = 15
LR           = 5e-5
WARMUP_RATIO = 0.1


# ── Dataset ───────────────────────────────────────────────────────────────────
class SignLanguageDataset(torch.utils.data.Dataset):
    def __init__(self, samples: list[tuple[Path, int]], processor):
        self.samples   = samples
        self.processor = processor

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        video_path, label = self.samples[idx]
        frames = _extract_frames(video_path)
        inputs = self.processor(frames, return_tensors="pt")
        return {
            "pixel_values": inputs["pixel_values"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
        }


def _extract_frames(video_path: Path) -> list:
    """Extrae NUM_FRAMES uniformes del clip con PyAV."""
    try:
        import av
        frames = []
        container = av.open(str(video_path))
        for frame in container.decode(video=0):
            frames.append(frame.to_ndarray(format="rgb24"))
        container.close()

        if not frames:
            return [np.zeros((224, 224, 3), dtype=np.uint8)] * NUM_FRAMES

        indices = np.linspace(0, len(frames) - 1, NUM_FRAMES, dtype=int)
        return [frames[i] for i in indices]

    except Exception as e:
        logger.warning("Error extrayendo frames de %s: %s", video_path.name, e)
        return [np.zeros((224, 224, 3), dtype=np.uint8)] * NUM_FRAMES


def _load_samples() -> tuple[list, list, list]:
    """Escanea CLIPS_DIR y divide en train/val/test (70/15/15)."""
    train, val, test = [], [], []

    if not CLIPS_DIR.exists():
        logger.error("No se encontró el directorio de clips: %s", CLIPS_DIR)
        sys.exit(1)

    for folder in sorted(CLIPS_DIR.iterdir()):
        if not folder.is_dir():
            continue

        raw_name  = folder.name
        canonical = FOLDER_ALIAS.get(raw_name, raw_name)

        if canonical not in LABEL2ID:
            logger.warning("Carpeta desconocida: '%s' → ignorada", raw_name)
            continue

        label = LABEL2ID[canonical]
        clips = sorted(folder.glob("*.webm"))
        n     = len(clips)

        if n == 0:
            logger.warning("Sin clips en: %s", folder)
            continue

        n_train = max(1, round(n * 0.70))
        n_val   = max(1, round(n * 0.15))
        n_test  = n - n_train - n_val

        for i, clip in enumerate(clips):
            if i < n_train:
                train.append((clip, label))
            elif i < n_train + n_val:
                val.append((clip, label))
            else:
                test.append((clip, label))

        logger.info(
            "  %-12s : %2d clips  →  %d train / %d val / %d test",
            canonical, n, n_train, n_val, max(0, n_test),
        )

    return train, val, test


# ── Entrenamiento ─────────────────────────────────────────────────────────────
def train(epochs: int, batch_size: int, push_to_hub: bool, hf_token: str):
    from transformers import (
        VideoMAEForVideoClassification,
        VideoMAEImageProcessor,
        TrainingArguments,
        Trainer,
    )
    import evaluate as hf_evaluate

    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info("=" * 55)
    logger.info("Sprint 3 – Fine-tuning VideoMAE")
    logger.info("  Base model : %s", BASE_MODEL)
    logger.info("  Clases     : %d", len(PALABRAS_MVP))
    logger.info("  Frames     : %d", NUM_FRAMES)
    logger.info("  Epochs     : %d", epochs)
    logger.info("  Batch size : %d", batch_size)
    logger.info("  Dispositivo: %s", device.upper())
    if device == "cpu":
        logger.warning("  Sin GPU detectada. Considera usar Google Colab con T4.")
    logger.info("=" * 55)

    # ── Processor y modelo ─────────────────────────────────────────
    logger.info("Cargando %s ...", BASE_MODEL)
    processor = VideoMAEImageProcessor.from_pretrained(BASE_MODEL)
    model = VideoMAEForVideoClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(PALABRAS_MVP),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,  # reemplaza la cabeza de 400 clases por 15
    )
    model.to(device)

    # ── Dataset ────────────────────────────────────────────────────
    logger.info("Cargando dataset desde: %s", CLIPS_DIR)
    train_samples, val_samples, test_samples = _load_samples()
    logger.info(
        "Total → train=%d  val=%d  test=%d",
        len(train_samples), len(val_samples), len(test_samples),
    )

    if len(train_samples) == 0:
        logger.error("No hay muestras de entrenamiento. Verifica %s", CLIPS_DIR)
        sys.exit(1)

    train_ds = SignLanguageDataset(train_samples, processor)
    val_ds   = SignLanguageDataset(val_samples,   processor)

    # ── Métricas ───────────────────────────────────────────────────
    accuracy_metric = hf_evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return accuracy_metric.compute(predictions=preds, references=labels)

    # ── Carpetas de salida ─────────────────────────────────────────
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    hub_model_id = os.getenv("HF_MODEL_ID", "villarroel/videomae-sign-language-mvp")

    training_args = TrainingArguments(
        output_dir=str(CHECKPOINT_DIR),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=LR,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        logging_dir=str(CHECKPOINT_DIR / "logs"),
        logging_steps=5,
        fp16=device == "cuda",
        dataloader_num_workers=0,  # Windows requiere 0
        report_to="none",
        push_to_hub=push_to_hub,
        hub_model_id=hub_model_id if push_to_hub else None,
        hub_token=hf_token or None,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )

    # ── Entrenamiento ──────────────────────────────────────────────
    logger.info("Iniciando entrenamiento...")
    trainer.train()

    # ── Evaluación en test ─────────────────────────────────────────
    metrics: dict = {}
    if test_samples:
        test_ds     = SignLanguageDataset(test_samples, processor)
        test_result = trainer.evaluate(test_ds, metric_key_prefix="test")
        logger.info("Test accuracy : %.4f", test_result.get("test_accuracy", 0))
        metrics.update(test_result)

    val_result = trainer.evaluate(metric_key_prefix="val")
    logger.info("Val  accuracy : %.4f", val_result.get("val_accuracy", 0))
    metrics.update(val_result)
    metrics["num_classes"]  = len(PALABRAS_MVP)
    metrics["train_samples"] = len(train_samples)
    metrics["val_samples"]   = len(val_samples)
    metrics["test_samples"]  = len(test_samples)
    metrics["base_model"]    = BASE_MODEL
    metrics["epochs"]        = epochs

    metrics_path = METRICS_DIR / "train_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    logger.info("Métricas guardadas: %s", metrics_path)

    # ── Guardar checkpoint final ───────────────────────────────────
    best_dir = CHECKPOINT_DIR / "best"
    trainer.save_model(str(best_dir))
    processor.save_pretrained(str(best_dir))
    logger.info("Modelo guardado: %s", best_dir)

    if push_to_hub:
        trainer.push_to_hub()
        logger.info("Modelo subido a HF Hub: %s", hub_model_id)

    logger.info("=" * 55)
    logger.info("Entrenamiento completado.")
    logger.info("Para activar inferencia real en el backend:")
    logger.info("  backend/.env → APP_MODE=real")
    logger.info("  backend/.env → LOCAL_MODEL_PATH=models/checkpoints/videomae-sign-language/best")
    if push_to_hub:
        logger.info("  backend/.env → HF_MODEL_ID=%s", hub_model_id)
    logger.info("  Reinicia el servidor: uvicorn main:app --reload")
    logger.info("=" * 55)


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tuning VideoMAE – Sprint 3")
    parser.add_argument("--epochs",     type=int,  default=EPOCHS,     help="Número de épocas")
    parser.add_argument("--batch-size", type=int,  default=BATCH_SIZE, help="Tamaño de batch")
    parser.add_argument("--push-hub",   action="store_true",           help="Subir modelo a HF Hub")
    parser.add_argument("--hf-token",   default=os.getenv("HUGGINGFACE_TOKEN", ""), help="Token HF Hub")
    args = parser.parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        push_to_hub=args.push_hub,
        hf_token=args.hf_token,
    )
