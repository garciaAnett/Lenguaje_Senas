"""
seed_dataset.py – Sprint 2
Inicializa la estructura del dataset y genera el dataset_index.csv
con 10 entradas por cada una de las 7 palabras de Rodrigo (70 filas en total).
Los video_path apuntan a donde se guardarán los clips reales.

Uso (desde la carpeta backend/):
    python scripts/seed_dataset.py
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT  = Path(__file__).parent.parent.parent
DATASET_DIR   = PROJECT_ROOT / "dataset"
RAW_DIR       = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"
CSV_PATH      = DATASET_DIR / "dataset_index.csv"

CSV_HEADERS = ["sample_id", "palabra", "class_id", "participante", "video_path", "duracion", "fps", "split"]

# 7 palabras de Rodrigo (primeras del MVP)
PALABRAS_RODRIGO = [
    {"palabra": "Hola",    "class_id": 0},
    {"palabra": "Gracias", "class_id": 1},
    {"palabra": "Sí",      "class_id": 2},
    {"palabra": "No",      "class_id": 3},
    {"palabra": "Ayuda",   "class_id": 4},
    {"palabra": "Agua",    "class_id": 5},
    {"palabra": "Comida",  "class_id": 6},
]

# Todas las carpetas necesarias (15 palabras del MVP)
TODAS_LAS_PALABRAS_DIRS = [
    "hola", "gracias", "si", "no", "ayuda", "agua", "comida",
    "bano", "casa", "escuela", "amigo", "familia", "perdon", "por_favor", "adios",
]

SAMPLES_PER_CLASS = 10

# Asignación de split: pos 0-6 → train, 7-8 → val, 9 → test
def split_for(pos: int) -> str:
    if pos < 7:
        return "train"
    elif pos < 9:
        return "val"
    return "test"


def create_dirs():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    for folder in TODAS_LAS_PALABRAS_DIRS:
        (RAW_DIR / folder).mkdir(parents=True, exist_ok=True)
        (PROCESSED_DIR / folder).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Carpetas creadas en: {DATASET_DIR}")


def generate_csv():
    # Leer entradas existentes para no duplicar
    existing_ids: set[str] = set()
    existing_rows: list[dict] = []
    if CSV_PATH.exists():
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            existing_ids = {r["sample_id"] for r in existing_rows}

    # Detectar siguiente número R disponible
    rodrigo_nums = []
    for sid in existing_ids:
        if sid.startswith("R"):
            try:
                rodrigo_nums.append(int(sid[1:]))
            except ValueError:
                pass
    counter = max(rodrigo_nums, default=0) + 1

    new_rows = []
    for p in PALABRAS_RODRIGO:
        folder = p["palabra"].lower().replace(" ", "_")
        for pos in range(SAMPLES_PER_CLASS):
            sample_id = f"R{counter:03d}"
            if sample_id in existing_ids:
                counter += 1
                sample_id = f"R{counter:03d}"

            filename  = f"{sample_id}_{folder}.webm"
            video_path = f"dataset/raw/{folder}/{filename}"

            new_rows.append({
                "sample_id":    sample_id,
                "palabra":      p["palabra"],
                "class_id":     p["class_id"],
                "participante": "rodrigo",
                "video_path":   video_path,
                "duracion":     2.5,
                "fps":          30,
                "split":        split_for(pos),
            })
            counter += 1

    all_rows = existing_rows + new_rows

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"[OK] dataset_index.csv generado: {CSV_PATH}")
    print(f"     Entradas nuevas de Rodrigo : {len(new_rows)}")
    print(f"     Total entradas en CSV      : {len(all_rows)}")
    print()
    print("     Palabras de Rodrigo:")
    for p in PALABRAS_RODRIGO:
        clase_rows = [r for r in new_rows if r["palabra"] == p["palabra"]]
        t = sum(1 for r in clase_rows if r["split"] == "train")
        v = sum(1 for r in clase_rows if r["split"] == "val")
        te = sum(1 for r in clase_rows if r["split"] == "test")
        print(f"       [{p['class_id']:2d}] {p['palabra']:10s} : {t} train | {v} val | {te} test")


if __name__ == "__main__":
    print("=" * 55)
    print("  Seed Dataset – Sprint 2 | Rodrigo Villarroel")
    print("=" * 55)
    create_dirs()
    generate_csv()
    print()
    print("  Siguiente paso: graba los clips y subelos con")
    print("  POST /dataset/upload (o copialos manualmente a")
    print("  las carpetas dataset/raw/<palabra>/)")
    print("=" * 55)
