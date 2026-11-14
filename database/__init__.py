# database/__init__.py
from .conexion import obtener_conexion

# Definimos qué es lo que este paquete expone al mundo exterior
__all__ = ["obtener_conexion"]