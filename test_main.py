from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor
from main import app
import pytest
import uuid
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
def evento_prueba(perfil_prueba):
    conn = None
    try:    
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        valores_evento = ("Nombre_falso", "ubicacion_falsa", perfil_prueba['id'])
        cursor.execute("""
                        INSERT INTO eventos (nombre_evento, ubicacion_evento, fecha_hora, perfil_id)
                        VALUES(%s, %s, NOW(), %s)
                        RETURNING id 
                        """, (valores_evento))
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
                        WHERE id = %s;
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

def test_evento_sin_invitados_devuelve_lista_vacia(evento_prueba, headers_auth):
    respuesta = client.get(f"/invitados?evento_id={evento_prueba}", headers=headers_auth)

    assert respuesta.status_code == 200
    assert respuesta.json() == []

def test_evento_inexistente_error(headers_auth):
    respuesta = client.get("/invitados?evento_id=999999999", headers=headers_auth)

    assert respuesta.status_code == 404
    assert respuesta.json()['detail'] == "El evento no existe"

def test_listar_invitados_con_un_invitado(evento_prueba, headers_auth):
    client.post("/invitados", json={"nombre":"gina", "telefono":"6675665643", "evento_fk":evento_prueba})
    lista_invitado_evento = client.get(f"/invitados?evento_id={evento_prueba}", headers=headers_auth)

    assert lista_invitado_evento.status_code == 200
    assert len(lista_invitado_evento.json()) == 1
    assert lista_invitado_evento.json()[0]['nombre'] == "gina"

def test_verificar_qr(evento_prueba):
    respuesta = client.post("/invitados", json={"nombre":"gina", "telefono":"6675665643", "evento_fk":evento_prueba})
    invitado_id = respuesta.json()['id']
    qr = client.get(f"/invitados/{invitado_id}/qr")

    assert qr.status_code == 200
    assert qr.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert qr.headers["content-type"] == "image/png"

def test_invitado_que_no_existe():
    respuesta = client.get("/invitados/999999/qr")

    assert respuesta.status_code == 404
    assert respuesta.json()['detail'] == "El invitado no existe"

@pytest.fixture
def perfil_prueba():
    usuario = f"perfil_{uuid.uuid4().hex[:8]}"
    password = f"clave_{uuid.uuid4().hex[:8]}"

    respuesta = client.post("/registro", json={"usuario":usuario, "password": password})
    perfil_id = respuesta.json()['id']

    yield {"id":perfil_id, "usuario":usuario, "password":password}

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                        DELETE FROM perfiles
                        WHERE id = %s
                        """,(perfil_id, ))
        conn.commit()
        cursor.close()

    finally:
        if conn:
            conn.close()

def test_registro_usuario_repetido(perfil_prueba):
    respuesta = client.post("/registro", json={"usuario":perfil_prueba['usuario'],"password":perfil_prueba['password']})

    assert respuesta.status_code == 409
    assert respuesta.json()['detail'] == "El usuario ya existe"

def test_registro_password_corta():
    respuesta = client.post("/registro", json={"usuario":"usuario_sin_guardar", "password": "corta"})

    assert respuesta.status_code == 422
    assert respuesta.json()['detail'][0]['loc'] == ["body", "password"]
    assert respuesta.json()['detail'][0]['type'] == "string_too_short"

def test_login_correcto(perfil_prueba):
    respuesta = client.post("/login", json={"usuario":perfil_prueba["usuario"], "password":perfil_prueba['password']})

    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()
    assert respuesta.json()['token_type'] == "bearer"

def test_login_password_incorrecta(perfil_prueba):
    respuesta = client.post("/login", json={"usuario":perfil_prueba['usuario'], "password":"otra_clave"})

    assert respuesta.status_code == 401
    assert respuesta.json()['detail'] == "Usuario o Contrasena Incorrectos"

def test_login_usuario_inexistente():
    respuesta = client.post("/login", json={"usuario":"usuario_falso", "password":"password_falsa"})

    assert respuesta.status_code == 401
    assert respuesta.json()['detail'] == "Usuario o Contrasena Incorrectos"

def test_registro_usuario_nuevo():
    usuario = f"perfil_{uuid.uuid4().hex[:8]}"
    password = f"clave_{uuid.uuid4().hex[:8]}"

    respuesta = client.post("/registro", json={"usuario":usuario, "password":password})
    usuario_id = respuesta.json()['id']
    
    try:
        assert respuesta.status_code == 200
        assert respuesta.json()['usuario'] == usuario
        assert "password_hash" not in respuesta.json()

    finally:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                        DELETE FROM perfiles
                        WHERE id = %s
                        """, (usuario_id,))
        
            conn.commit()
            cursor.close()
            
        finally:
            if conn:
                conn.close()

@pytest.fixture
def headers_auth(perfil_prueba):
    respuesta = client.post("/login", json={"usuario":perfil_prueba['usuario'], "password":perfil_prueba['password']})
    token  = respuesta.json()['access_token']

    return {"Authorization": f"Bearer {token}"}

def test_listar_invitado_sin_token():
    respuesta = client.get("/invitados?evento_id=1")
    
    assert respuesta.status_code == 401
    assert respuesta.json()['detail'] == "Token requerido"