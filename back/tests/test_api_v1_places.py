from fastapi.testclient import TestClient
import pandas as pd
import pytest

from back.main import app
from back.storage import places_repo


@pytest.fixture(autouse=True)
def temp_places_csv(tmp_path, monkeypatch):
    """Fixture que redirige el CSV de places a un archivo temporal vacío."""
    csv_path = tmp_path / "places.csv"
    # Crear CSV con cabeceras esperadas
    df = pd.DataFrame(columns=[
        'id', 'nombre', 'direccion', 'codigo_casino', 'estado',
        'created_at', 'created_by', 'updated_at', 'updated_by'
    ])
    df.to_csv(csv_path, index=False)
    monkeypatch.setattr(places_repo, "PLACES_CSV", csv_path)
    yield


client = TestClient(app)


def test_create_and_search_place():
    payload = {
        "nombre": "Casino Central",
        "direccion": "Calle Falsa 123, Ciudad",
        "codigo_casino": "cc01"
    }

    r = client.post("/api/v1/places/casino", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert data["nombre"] == "Casino Central"
    assert data["codigo_casino"] == "CC01"
    assert data["estado"] is True

    # Buscar por texto en nombre
    r2 = client.get("/api/v1/places/casino", params={"consulta": "central"})
    assert r2.status_code == 200
    lista = r2.json()
    assert isinstance(lista, list)
    assert len(lista) >= 1
    assert any(item["nombre"] == "Casino Central" for item in lista)


def test_update_ignores_codigo_casino_and_updates_nombre():
    # Crear
    payload = {
        "nombre": "Casino Old",
        "direccion": "Calle Falsa 456, Ciudad",
        "codigo_casino": "OLD1"
    }
    r = client.post("/api/v1/places/casino", json=payload)
    assert r.status_code == 200
    data = r.json()
    id_lugar = data["id"]

    # Intentar actualizar codigo_casino (se enviará pero el modelo de actualización no lo acepta)
    update_payload = {
        "codigo_casino": "NEWCODE",  # campo extra: debe ser ignorado por PlaceUpdate
        "nombre": "Casino Nuevo"
    }
    r2 = client.put(f"/api/v1/places/casino/{id_lugar}", json=update_payload)
    assert r2.status_code == 200
    updated = r2.json()
    # codigo_casino debe permanecer inalterado
    assert updated["codigo_casino"] == "OLD1"
    assert updated["nombre"] == "Casino Nuevo"


def test_inactivate_and_filter_by_estado():
    # Crear
    payload = {
        "nombre": "Casino To Inactivate",
        "direccion": "Avenida Principal 1000, Ciudad",
        "codigo_casino": "TOIN"
    }
    r = client.post("/api/v1/places/casino", json=payload)
    assert r.status_code == 200
    id_lugar = r.json()["id"]

    # Inactivar
    r2 = client.put(f"/api/v1/places/casino/{id_lugar}/inactivar")
    assert r2.status_code == 200
    body = r2.json()
    assert body.get("mensaje")

    # Listar solo activos (debe excluirlo)
    r3 = client.get("/api/v1/places/casino", params={"solo_activos": True})
    assert r3.status_code == 200
    activos = r3.json()
    assert all(item["estado"] for item in activos)
    assert not any(item["id"] == id_lugar for item in activos)

    # Listar incluyendo inactivos
    r4 = client.get("/api/v1/places/casino", params={"solo_activos": False})
    assert r4.status_code == 200
    todos = r4.json()
    assert any(item["id"] == id_lugar for item in todos)
