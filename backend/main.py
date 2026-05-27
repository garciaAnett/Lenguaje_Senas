"""
MVP Traducción de Lenguaje de Señas
Backend FastAPI - Sprint 1
Autor: Rodrigo Villarroel
Fecha: 27/05/2026
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import health, predict
from models.model_manager import ModelManager

# ──────────────────────────────────────────────
# Lifecycle: carga el modelo al arrancar
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[INFO] Iniciando backend de traduccion de lenguaje de senas...")
    app.state.model_manager = ModelManager()
    await app.state.model_manager.load()
    print("[INFO] Backend listo.")
    yield
    # Shutdown
    print("[INFO] Cerrando backend...")


# ──────────────────────────────────────────────
# App
# ──────────────────────────────────────────────
app = FastAPI(
    title="Sign Language MVP API",
    description=(
        "API para traducción de lenguaje de señas usando VideoMAE + Hugging Face. "
        "Sprint 1: endpoints /health y /predict (modo mock)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS – permite que React/Vite consuma la API en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Predicción"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "mensaje": "Sign Language MVP API activa",
        "docs": "/docs",
        "version": "0.1.0",
        "sprint": 1,
        "modo": "mock",
    }
