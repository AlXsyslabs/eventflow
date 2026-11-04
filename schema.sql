CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    nombre_evento TEXT NOT NULL,
    ubicacion_evento TEXT, 
    fecha_hora TIMESTAMP NOT NULL
);

CREATE TABLE invitados (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    puesto TEXT,
    telefono TEXT NOT NULL,
    correo TEXT,
    patrocinador TEXT,
    ingreso TIMESTAMP,
    evento_fk INTEGER NOT NULL REFERENCES eventos(id)
);