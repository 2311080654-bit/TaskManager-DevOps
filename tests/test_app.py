import os
import tempfile
import pytest

# Usar una base de datos temporal antes de importar app
db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_PATH"] = db_path

from app import app, init_db  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client


def test_cp01_registrar_tarea(client):
    res = client.post(
        "/api/tareas",
        json={
            "nombre": "Elaborar documentación",
            "descripcion": "Documentar fases DevOps",
            "prioridad": "Alta",
        },
    )
    data = res.get_json()
    assert res.status_code == 201
    assert data["tarea"]["nombre"] == "Elaborar documentación"
    assert data["tarea"]["estado"] == "Pendiente"
    assert data["tarea"]["prioridad"] == "Alta"


def test_cp02_registrar_tarea_sin_nombre(client):
    res = client.post("/api/tareas", json={"nombre": "", "prioridad": "Media"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_cp03_consultar_tareas(client):
    res = client.get("/api/tareas")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    assert len(res.get_json()) >= 1


def test_cp04_y_cp06_editar_y_cambiar_estado(client):
    crear = client.post("/api/tareas", json={"nombre": "Tarea inicial", "prioridad": "Baja"}).get_json()
    tid = crear["tarea"]["id"]

    res = client.put(
        f"/api/tareas/{tid}",
        json={"nombre": "Tarea editada", "estado": "Terminada", "prioridad": "Alta"},
    )
    actualizada = res.get_json()["tarea"]
    assert res.status_code == 200
    assert actualizada["nombre"] == "Tarea editada"
    assert actualizada["estado"] == "Terminada"
    assert actualizada["prioridad"] == "Alta"


def test_cp05_eliminar_tarea(client):
    crear = client.post("/api/tareas", json={"nombre": "Tarea a borrar"}).get_json()
    tid = crear["tarea"]["id"]

    res_del = client.delete(f"/api/tareas/{tid}")
    assert res_del.status_code == 200

    res_get = client.put(f"/api/tareas/{tid}", json={"estado": "En proceso"})
    assert res_get.status_code == 404