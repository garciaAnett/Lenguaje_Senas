"""
Tests unitarios – Sprint 1
Ejecutar con: pytest tests/ -v
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200
    assert r.json()["sprint"] == 1


@pytest.mark.anyio
async def test_health_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["modo"] == "mock"
    assert len(data["palabras_soportadas"]) == 15
    assert "Hola" in data["palabras_soportadas"]
    assert "Adiós" in data["palabras_soportadas"]


@pytest.mark.anyio
async def test_predict_palabras():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/predict/palabras")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 15
    palabras = [p["palabra"] for p in data["palabras"]]
    for expected in ["Hola", "Gracias", "Sí", "No", "Ayuda", "Agua",
                     "Comida", "Baño", "Casa", "Escuela",
                     "Amigo", "Familia", "Perdón", "Por favor", "Adiós"]:
        assert expected in palabras


@pytest.mark.anyio
async def test_predict_mock_mp4():
    """Envía un MP4 mínimo (cabecera válida) y verifica la respuesta mock."""
    # Bytes mínimos que pasan la validación de tipo y tamaño
    fake_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 100

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/predict",
            files={"video": ("test.mp4", fake_video, "video/mp4")},
        )
    assert r.status_code == 200
    data = r.json()
    assert "prediccion" in data
    assert "top3" in data
    assert data["modo"] == "mock"
    assert 0.0 <= data["prediccion"]["confianza"] <= 1.0
    assert len(data["top3"]) == 3


@pytest.mark.anyio
async def test_predict_empty_file():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/predict",
            files={"video": ("empty.mp4", b"", "video/mp4")},
        )
    assert r.status_code == 400


@pytest.mark.anyio
async def test_predict_invalid_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/predict",
            files={"video": ("image.jpg", b"\xff\xd8\xff" + b"\x00" * 100, "image/jpeg")},
        )
    assert r.status_code == 415
