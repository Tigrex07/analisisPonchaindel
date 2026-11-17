# database/conexion.py
import sqlite3
import os

DB_NAME = "rrhh_lite.db"

def obtener_conexion():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_base_datos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # 1. Tabla maestros con area y sindicalizado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maestros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT DEFAULT 'NORMAL',
            activo INTEGER DEFAULT 1,
            area TEXT DEFAULT 'Tecnologías de la Información',
            sindicalizado INTEGER DEFAULT 0
        )
    """)
    
    # Migración segura por si la tabla ya existía sin estas columnas
    cursor.execute("PRAGMA table_info(maestros)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'area' not in columns:
        cursor.execute("ALTER TABLE maestros ADD COLUMN area TEXT DEFAULT 'Tecnologías de la Información'")
    if 'sindicalizado' not in columns:
        cursor.execute("ALTER TABLE maestros ADD COLUMN sindicalizado INTEGER DEFAULT 0")

    # 2. Tabla ponchadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ponchadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idMaestro INTEGER,
            fecha TEXT,
            hora TEXT,
            tipo TEXT,
            FOREIGN KEY(idMaestro) REFERENCES maestros(id)
        )
    """)

    # 3. Tabla horarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idMaestro INTEGER,
            dia_semana TEXT,
            hora_entrada TEXT,
            hora_salida TEXT,
            FOREIGN KEY(idMaestro) REFERENCES maestros(id)
        )
    """)

    # 4. Tablas para Listas Personalizadas (Relación Muchos a Muchos independiente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listas_personalizadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_lista_maestros (
            id_lista INTEGER,
            id_maestro INTEGER,
            PRIMARY KEY(id_lista, id_maestro),
            FOREIGN KEY(id_lista) REFERENCES listas_personalizadas(id) ON DELETE CASCADE,
            FOREIGN KEY(id_maestro) REFERENCES maestros(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

# Ejecutar inicialización al importar
inicializar_base_datos()