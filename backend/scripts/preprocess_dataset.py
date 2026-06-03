"""
preprocess_dataset.py – Sprint 2 (stub) / Sprint 3 (activo)
Lee el dataset_index.csv y preprocesa los clips crudos:
  • Redimensiona a 224×224
  • Normaliza a TARGET_FPS (15)
  • Extrae TARGET_FRAMES (16) frames uniformemente distribuidos
  • Guarda en dataset/processed/<palabra>/

Sprint 2: estructura preparada, la función de conversión es un stub.
Sprint 3: descomentar el bloque OpenCV para activar el preprocesamiento real.

Uso (desde la carpeta backend/):
    python scripts/preprocess_dataset.py
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT  = Path(__file__).parent.parent.parent
DATASET_DIR   = PROJECT_ROOT / "dataset"
RAW_DIR       = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"
CSV_PATH      = DATASET_DIR / "dataset_index.csv"

TARGET_FPS    = 15
TARGET_SIZE   = (224, 224)
TARGET_FRAMES = 16


def preprocess_clip(raw_path: Path, processed_path: Path) -> bool:
    """
    Convierte un clip crudo en una versión normalizada para el modelo.
    Sprint 3: descomentar cuando opencv-python esté instalado.
    """
    # ── Sprint 3: descomentar este bloque ───────────────────────────
    # import cv2
    # import numpy as np
    #
    # cap = cv2.VideoCapture(str(raw_path))
    # total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # if total == 0:
    #     cap.release()
    #     return False
    #
    # indices = np.linspace(0, total - 1, TARGET_FRAMES, dtype=int)
    # processed_path.parent.mkdir(parents=True, exist_ok=True)
    #
    # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    # out = cv2.VideoWriter(str(processed_path), fourcc, TARGET_FPS, TARGET_SIZE)
    # for idx in indices:
    #     cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
    #     ret, frame = cap.read()
    #     if ret:
    #         frame = cv2.resize(frame, TARGET_SIZE)
    #         out.write(frame)
    # cap.release()
    # out.release()
    # return True
    # ────────────────────────────────────────────────────────────────

    print(f"    [stub] {raw_path.name} → (Sprint 3: activar con OpenCV)")
    return False


def run():
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV no encontrado: {CSV_PATH}")
        print("  Ejecuta primero: python scripts/seed_dataset.py")
        sys.exit(1)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print("=" * 55)
    print(f"  Preprocesamiento – {len(rows)} clips en el CSV")
    print(f"  Target: {TARGET_FRAMES} frames | {TARGET_SIZE} px | {TARGET_FPS} fps")
    print("=" * 55)

    ok = skipped_no_file = skipped_exists = 0

    for row in rows:
        raw_path = PROJECT_ROOT / row["video_path"]
        folder   = row["palabra"].lower().replace(" ", "_")
        stem     = Path(row["video_path"]).stem
        proc_path = PROCESSED_DIR / folder / f"{stem}_processed.mp4"

        if not raw_path.exists():
            print(f"  [pendiente] {row['sample_id']} — clip no grabado aún")
            skipped_no_file += 1
            continue

        if proc_path.exists():
            skipped_exists += 1
            continue

        success = preprocess_clip(raw_path, proc_path)
        if success:
            ok += 1

    print()
    print(f"  Procesados  : {ok}")
    print(f"  Ya existían : {skipped_exists}")
    print(f"  Pendientes  : {skipped_no_file} (clips no grabados)")

    if skipped_no_file > 0:
        print()
        print("  Graba los clips pendientes y vuelve a ejecutar este script.")


if __name__ == "__main__":
    run()
