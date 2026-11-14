# views/__init__.py
from .dashboard_kpis import VistaKPIs
from .limpiador_csv import VistaLimpiadorCSV
from .horarios import VistaHorarios

# Definimos las clases que están disponibles para importar
__all__ = ["VistaKPIs", "VistaLimpiadorCSV"]