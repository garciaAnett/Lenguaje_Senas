"""
Configuración de pytest: inicializa el estado de la app antes de cada test.
El AsyncClient de httpx no dispara el lifespan de FastAPI por defecto,
así que lo hacemos manualmente con un fixture autouse.
"""

import pytest
from models.model_manager import ModelManager
from main import app


@pytest.fixture(autouse=True)
async def setup_app_state():
    """Inicializa app.state.model_manager antes de cada test."""
    manager = ModelManager()
    await manager.load()
    app.state.model_manager = manager
    yield
    # Limpieza (opcional)
    if hasattr(app.state, "model_manager"):
        del app.state.model_manager
