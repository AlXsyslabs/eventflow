from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor
from main import app
import pytest
from db import get_connection

client = TestClient(app)


def test_health():
    respuesta = client.get("/health")
    
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}

def test_agregar_invitado_error():
    respuesta = client.post("/invitados", json={"telefono": "6677865", "evento_fk":9})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "nombre"]
    assert respuesta.json()["detail"][0]["type"] == "missing"

@pytest.fixture
def evento_prueba():
    conn = None
    try:    
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        valores = ("Nombre_falso", "ubicacion_falsa")
        cursor.execute("""
                        INSERT INTO eventos (nombre_evento, ubicacion_evento, fecha_hora)
                        VALUES(%s, %s, NOW())
                        RETURNING id 
                        """, (valores))
        evento_id = cursor.fetchone()['id']
        conn.commit()
    
    finally:
        if conn:
            conn.close()

    yield evento_id

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                        DELETE FROM invitados
                        WHERE evento_fk = %s;
                        DELETE FROM eventos
                        WHERE id = %s
                        """, (evento_id, evento_id))
        conn.commit()
        cursor.close()

    finally:
        if conn:
            conn.close()


def test_agregar_invitado_ok(evento_prueba):
    respuesta = client.post("/invitados", json={"nombre":"gina", "telefono":"6675665643", "evento_fk":evento_prueba})

    assert respuesta.status_code == 200
    assert "id" in respuesta.json()


def test_ingreso_solo_una_vez(evento_prueba):
    creado = client.post("/invitados", json={"nombre":"gina", "telefono":"6675665643", "evento_fk":evento_prueba})

    assert creado.status_code == 200
    assert "id" in creado.json()
    invitado_id = creado.json()['id']

    primera = client.patch(f"/invitados/{invitado_id}/ingreso")
    assert primera.status_code == 200
    assert primera.json()['id'] == invitado_id

    segunda = client.patch(f"/invitados/{invitado_id}/ingreso")
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "Ya ingresó o no se registró"

def test_agregar_invitado_nombre_validacion():
    respuesta = client.post("/invitados", json={"nombre":"   ", "telefono":"6675645454", "evento_fk":2})
    assert respuesta.status_code == 422
    assert respuesta.json()['detail'][0]['loc'] == ["body", "nombre"]
    assert respuesta.json()['detail'][0]['type'] == "string_too_short"