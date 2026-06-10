"""
MVP Traducción de Lenguaje de Señas
Backend FastAPI - Sprint 2
Autores: Rodrigo Villarroel, Anett Garcia
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import health, predict, dataset
from models.model_manager import ModelManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Iniciando backend de traduccion de lenguaje de senas...")
    app.state.model_manager = ModelManager()
    await app.state.model_manager.load()
    print("[INFO] Backend listo.")
    yield
    print("[INFO] Cerrando backend...")


app = FastAPI(
    title="Sign Language MVP API",
    description=(
        "API para traducción de lenguaje de señas usando VideoMAE + Hugging Face. "
        "Sprint 3: inferencia real con modelo fine-tuned. APP_MODE=real para activar."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

# CORS – permite cualquier puerto de localhost en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Predicción"])
app.include_router(dataset.router)


@app.get("/", tags=["Root"])
async def root():
    import os
    return {
        "mensaje": "Sign Language MVP API activa",
        "docs": "/docs",
        "version": "0.3.0",
        "sprint": 3,
        "modo": os.getenv("APP_MODE", "mock"),
    }
