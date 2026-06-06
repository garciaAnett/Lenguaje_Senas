"""
Utilidades para gestión del dataset de señas.
Sprint 2: guardar clips, gestionar CSV, splits 70/15/15.
"""

import csv
import logging
import random
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Rutas base del proyecto
PROJECT_ROOT  = Path(__file__).parent.parent.parent
DATASET_DIR   = PROJECT_ROOT / "dataset"
RAW_DIR       = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"
CSV_PATH      = DATASET_DIR / "dataset_index.csv"

CSV_HEADERS = ["sample_id", "palabra", "class_id", "participante", "video_path", "duracion", "fps", "split"]

# Palabras del MVP con su class_id
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

CLASE_MAP = {p["palabra"]: p["class_id"] for p in PALABRAS_MVP}

SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}


# ──────────────────────────────────────────────
# Inicialización de estructura
# ──────────────────────────────────────────────

def _ensure_dirs():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for p in PALABRAS_MVP:
        folder = p["palabra"].lower().replace(" ", "_")
        (RAW_DIR / folder).mkdir(parents=True, exist_ok=True)
        (PROCESSED_DIR / folder).mkdir(parents=True, exist_ok=True)


def _ensure_csv():
    _ensure_dirs()
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


# ──────────────────────────────────────────────
# Lectura / escritura del CSV
# ──────────────────────────────────────────────

def load_dataset_index() -> list[dict]:
    """Carga todas las entradas del CSV como lista de dicts."""
    _ensure_csv()
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "sample_id":   row["sample_id"],
                "palabra":     row["palabra"],
                "class_id":    int(row["class_id"]),
                "participante": row["participante"],
                "video_path":  row["video_path"],
                "duracion":    float(row["duracion"]),
                "fps":         int(row["fps"]),
                "split":       row["split"],
            })
    return rows


def _save_all_rows(rows: list[dict]):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


# ──────────────────────────────────────────────
# Lógica de split
# ──────────────────────────────────────────────

def _assign_split(rows: list[dict], palabra: str) -> str:
    """Asigna split para mantener la proporción 70/15/15 por clase."""
    clase = [r for r in rows if r["palabra"] == palabra]
    n = len(clase)
    if n == 0:
        return "train"

    train = sum(1 for r in clase if r["split"] == "train")
    val   = sum(1 for r in clase if r["split"] == "val")

    ratio_train = train / n
    ratio_val   = val / n

    if ratio_train < SPLIT_RATIOS["train"]:
        return "train"
    elif ratio_val < SPLIT_RATIOS["val"]:
        return "val"
    else:
        return "test"


def _next_sample_id(rows: list[dict], participante: str) -> str:
    prefix = "R" if participante.lower().startswith("r") else "A"
    nums = []
    for r in rows:
        if r["sample_id"].startswith(prefix):
            try:
                nums.append(int(r["sample_id"][1:]))
            except ValueError:
                pass
    return f"{prefix}{(max(nums, default=0) + 1):03d}"


# ──────────────────────────────────────────────
# Operaciones principales
# ──────────────────────────────────────────────

async def save_clip(
    video_bytes: bytes,
    palabra: str,
    participante: str,
    duracion: float,
    fps: int,
    original_filename: str,
) -> dict:
    """Guarda el clip en disco y agrega la entrada al CSV. Devuelve el dict de la entrada."""
    from fastapi import HTTPException

    if palabra not in CLASE_MAP:
        raise HTTPException(status_code=400, detail=f"Palabra '{palabra}' no está en el MVP.")

    rows = load_dataset_index()
    sample_id = _next_sample_id(rows, participante)
    split = _assign_split(rows, palabra)

    ext = Path(original_filename).suffix or ".webm"
    folder = palabra.lower().replace(" ", "_")
    filename = f"{sample_id}_{folder}{ext}"
    raw_path = RAW_DIR / folder / filename

    _ensure_dirs()
    with open(raw_path, "wb") as f:
        f.write(video_bytes)

    rel_path = str(raw_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

    entry = {
        "sample_id":    sample_id,
        "palabra":      palabra,
        "class_id":     CLASE_MAP[palabra],
        "participante": participante.lower(),
        "video_path":   rel_path,
        "duracion":     duracion,
        "fps":          fps,
        "split":        split,
    }
    rows.append(entry)
    _save_all_rows(rows)

    return entry


def update_csv_entry(sample_id: str, **kwargs) -> dict | None:
    """Actualiza campos de una entrada del CSV por sample_id."""
    rows = load_dataset_index()
    for i, r in enumerate(rows):
        if r["sample_id"] == sample_id:
            rows[i] = {**r, **kwargs}
            _save_all_rows(rows)
            return rows[i]
    return None


def compute_split() -> dict:
    """Redistribuye aleatoriamente los splits 70/15/15 por clase."""
    rows = load_dataset_index()
    if not rows:
        return {"total": 0, "train": 0, "val": 0, "test": 0}

    by_class: dict[str, list] = defaultdict(list)
    for r in rows:
        by_class[r["palabra"]].append(r)

    updated = []
    for palabra, clase_rows in by_class.items():
        random.shuffle(clase_rows)
        n = len(clase_rows)
        n_train = max(1, round(n * SPLIT_RATIOS["train"]))
        n_val   = max(1, round(n * SPLIT_RATIOS["val"]))

        for i, r in enumerate(clase_rows):
            if i < n_train:
                split = "train"
            elif i < n_train + n_val:
                split = "val"
            else:
                split = "test"
            updated.append({**r, "split": split})

    _save_all_rows(updated)

    return {
        "total": len(updated),
        "train": sum(1 for r in updated if r["split"] == "train"),
        "val":   sum(1 for r in updated if r["split"] == "val"),
        "test":  sum(1 for r in updated if r["split"] == "test"),
    }


def get_stats() -> dict:
    """Devuelve estadísticas del dataset."""
    rows = load_dataset_index()

    total = len(rows)
    train = sum(1 for r in rows if r["split"] == "train")
    val   = sum(1 for r in rows if r["split"] == "val")
    test  = sum(1 for r in rows if r["split"] == "test")

    palabras_en_dataset = {r["palabra"] for r in rows}
    todas = {p["palabra"] for p in PALABRAS_MVP}
    pendientes = sorted(todas - palabras_en_dataset)

    por_clase = []
    for p in PALABRAS_MVP:
        clase = [r for r in rows if r["palabra"] == p["palabra"]]
        por_clase.append({
            "palabra":  p["palabra"],
            "class_id": p["class_id"],
            "total":    len(clase),
            "train":    sum(1 for r in clase if r["split"] == "train"),
            "val":      sum(1 for r in clase if r["split"] == "val"),
            "test":     sum(1 for r in clase if r["split"] == "test"),
        })

    return {
        "total_clips":        total,
        "palabras_cubiertas": len(palabras_en_dataset),
        "splits":             {"train": train, "val": val, "test": test},
        "por_clase":          por_clase,
        "palabras_pendientes": pendientes,
    }
