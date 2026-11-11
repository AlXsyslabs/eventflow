from fastapi import FastAPI, HTTPException, Response
from typing import Annotated
from pydantic import BaseModel, StringConstraints
from db import get_connection
from psycopg2.extras import RealDictCursor
import io
import qrcode
app = FastAPI()


class InvitadoIn(BaseModel):
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    puesto  : str | None = None
    telefono : str
    correo : str | None = None
    es_patrocinador : bool = False
    evento_fk : int

@app.get("/health")
async def salud():
    return {"status": "ok"}


@app.post("/invitados")
def agregar_invitado(data: InvitadoIn):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        valores = (data.nombre, data.puesto, data.telefono, data.correo, data.es_patrocinador, data.evento_fk)
        cursor.execute(""" 
                    INSERT INTO invitados (nombre, puesto, telefono, correo, 
                    es_patrocinador, evento_fk) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id 
                    ;""", (valores)) 
        fila = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        return fila
    
    finally:
        if conn:
            conn.close()


@app.get("/invitados")
def listar_invitados(evento_id: int):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                        SELECT id FROM eventos
                        WHERE id = %s
                        """, (evento_id, ))
        fila = cursor.fetchone()   
        if fila is None:
            raise HTTPException(status_code=404, detail="El evento no existe")    
        
        cursor.execute("""
                        SELECT id, nombre, puesto, telefono, correo, 
                        es_patrocinador, ingreso, evento_fk FROM invitados 
                        WHERE evento_fk = %s ORDER BY id
                        """, (evento_id, ))
        lista = cursor.fetchall()
        
        return lista
    
    finally:
        if conn:
            conn.close()


@app.patch("/invitados/{invitado_id}/ingreso")
def actualizar_ingreso_invitado(invitado_id:int):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                        UPDATE invitados
                        SET ingreso = NOW()
                        WHERE id = %s AND ingreso IS NULL
                        RETURNING id
                        """, (invitado_id,))
        conn.commit()
        fila = cursor.fetchone()
        cursor.close()
        if fila is None:
            raise HTTPException(status_code=409, detail="Ya ingresó o no se registró")
        
        return fila
    
    finally:
        if conn:
            conn.close()


@app.get("/invitados/{invitado_id}/qr")
def invitado_qr(invitado_id:int):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                        SELECT id FROM invitados
                        WHERE id = %s
                        """, (invitado_id,))
        fila = cursor.fetchone()
        if fila is None:
            raise HTTPException(status_code=404, detail="El invitado no existe")
        
        image = qrcode.make(str(invitado_id))#crea un qr con el id del invitado
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        return Response(content=buffer.getvalue(), media_type="image/png")
    
    finally:
        if conn:
            conn.close()