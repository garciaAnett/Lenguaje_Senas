# 🤟 MVP Traducción de Lenguaje de Señas

> Aplicación web en tiempo real con **VideoMAE + Hugging Face**  
> Equipo: Anett Garcia · Rodrigo Villarroel  
> Stakeholder: Ing. Claudia Ureña

---

## 🗓️ Sprints

| Sprint | Fecha | Enfoque | Estado |
|--------|-------|---------|--------|
| 1 | 27/05/2026 | Base técnica del MVP | ✅ En curso |
| 2 | 03/06/2026 | Dataset de video | ⬜ Pendiente |
| 3 | 10/06/2026 | Modelo e integración | ⬜ Pendiente |
| 4 | 17/06/2026 | Cierre y demo | ⬜ Pendiente |

---

## 🏗️ Arquitectura

```
React/Vite (frontend)
    ↓  POST /predict  (clip MP4/WebM)
FastAPI (backend)
    ↓  Sprint 3: HF Hub
VideoMAE fine-tuned
    ↓  clase + confianza
FastAPI → React
```

---

## 📁 Estructura del repositorio

```
Lenguaje_Senas/
├── backend/                 ← FastAPI (Rodrigo)
│   ├── main.py              ← App principal
│   ├── routers/
│   │   ├── health.py        ← GET /health
│   │   └── predict.py       ← POST /predict
│   ├── models/
│   │   └── model_manager.py ← Gestión VideoMAE
│   ├── schemas/
│   │   └── prediction.py    ← Modelos Pydantic
│   ├── utils/
│   │   └── video_utils.py   ← Preprocesamiento
│   ├── tests/               ← pytest
│   ├── requirements.txt
│   └── .env.example
├── frontend/                ← React/Vite (Anett)
├── dataset/
│   ├── raw/                 ← Clips originales (no en repo)
│   ├── processed/           ← Clips preprocesados (no en repo)
│   └── dataset_index.csv    ← Índice del dataset ✅ en repo
└── README.md
```

---

## 🚀 Inicio rápido – Backend

### 1. Crear entorno virtual

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac
# Editar .env con tu token de Hugging Face (Sprint 3)
```

### 4. Ejecutar el servidor

```bash
uvicorn main:app --reload --port 8000
```

### 5. Probar la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info del servidor |
| `/health` | GET | Estado del servidor y modelo |
| `/predict` | POST | Clasificar clip de seña |
| `/predict/palabras` | GET | Listar 15 palabras |
| `/docs` | GET | Swagger UI automático |

---

## 🧪 Ejecutar tests

```bash
cd backend
pytest tests/ -v
```

---

## 🤖 Modelo – VideoMAE

- **Base:** `MCG-NJU/videomae-base` (Hugging Face)
- **Task:** Video Classification
- **Clases:** 15 palabras del MVP
- **Fine-tuning:** Sprint 3 (GPU requerida)
- **Dataset:** clips propios de 2–3 s, 15–30 fps

### 15 palabras del MVP

| class_id | Palabra |
|----------|---------|
| 0 | Hola |
| 1 | Gracias |
| 2 | Sí |
| 3 | No |
| 4 | Ayuda |
| 5 | Agua |
| 6 | Comida |
| 7 | Baño |
| 8 | Casa |
| 9 | Escuela |
| 10 | Amigo |
| 11 | Familia |
| 12 | Perdón |
| 13 | Por favor |
| 14 | Adiós |

---

## 🔗 Links del proyecto

- **Trello:** https://trello.com/invite/b/6a0a5e644863ac39b0f6d78e/...
- **GitHub:** https://github.com/garciaAnett/Lenguaje_Senas.git
- **HF Hub:** (pendiente Sprint 3)

---

## 📋 Dataset – `dataset_index.csv`

```
sample_id, palabra, class_id, participante, video_path, duracion, fps, split
```

División: 70% train · 15% val · 15% test  
*(El CSV se genera en Sprint 2)*
