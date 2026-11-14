# database/conexion.py
import sqlite3
import os

def obtener_conexion():
    ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_bd = os.path.join(ruta_raiz, "rrhh_lite.db")
    
    conn = sqlite3.connect(ruta_bd)
    _inicializar_bd(conn)
    return conn

def _inicializar_bd(conn):
    """Crea las tablas esenciales eliminando redundancias."""
    cursor = conn.cursor()
    
    # Tabla de Maestros simplificada (Solo ID, Nombre, Tipo y Activo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maestros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('NORMAL', 'PA')) DEFAULT 'NORMAL',
            activo INTEGER DEFAULT 1
        )
    ''')

    # Tabla de Ponchadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ponchadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idMaestro INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('ENTRADA', 'SALIDA', 'DESCONOCIDO')) DEFAULT 'DESCONOCIDO',
            FOREIGN KEY (idMaestro) REFERENCES maestros(id) ON DELETE CASCADE
        )
    ''')

    # Tabla de Horarios (Lista para el siguiente módulo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idMaestro INTEGER NOT NULL,
            dia_semana TEXT NOT NULL,
            hora_entrada TEXT,
            hora_salida TEXT,
            FOREIGN KEY (idMaestro) REFERENCES maestros(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()