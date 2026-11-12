CREATE TABLE perfiles(
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    nombre_evento TEXT NOT NULL,
    ubicacion_evento TEXT, 
    fecha_hora TIMESTAMPTZ NOT NULL ,
    perfil_id INTEGER NOT NULL REFERENCES perfiles(id)
);

CREATE TABLE invitados (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    puesto TEXT,
    telefono TEXT NOT NULL,
    correo TEXT,
    es_patrocinador BOOLEAN NOT NULL DEFAULT FALSE,
    ingreso TIMESTAMPTZ,
    evento_fk INTEGER NOT NULL REFERENCES eventos(id)
);