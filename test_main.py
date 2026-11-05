from fastapi.testclient import TestClient
from main import app

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