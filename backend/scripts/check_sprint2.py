"""Verificacion rapida de Sprint 2."""
import sys
sys.path.insert(0, ".")

from routers import dataset
from utils.dataset_utils import get_stats

print("Imports OK")
s = get_stats()
print(f"Dataset : {s['total_clips']} clips | {s['palabras_cubiertas']} palabras")
print(f"Splits  : train={s['splits']['train']} val={s['splits']['val']} test={s['splits']['test']}")
print(f"Pendientes: {s['palabras_pendientes']}")
