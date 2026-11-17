# main.py
import customtkinter as ctk

from views.dashboard_kpis import VistaKPIs
from views.metricas_reportes import VistaMetricasReportes
from views.limpiador_csv import VistaLimpiadorCSV
from views.configuracion import VistaConfiguracion

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integral de RRHH - Control y Analíticas UTN")
        self.geometry("1200x750")
        
        # Contenedor principal con el orden rediseñado
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_kpis = self.tabview.add("📊 Dashboard KPIs")
        self.tab_metricas = self.tabview.add("📈 Métricas y Reportes")
        self.tab_csv = self.tabview.add("📁 Limpiador CSV")
        self.tab_config = self.tabview.add("⚙️ Configuración")

        # Inicializar vistas
        self.vista_kpis = VistaKPIs(self.tab_kpis)
        self.vista_kpis.pack(fill="both", expand=True)

        self.vista_metricas = VistaMetricasReportes(self.tab_metricas)
        self.vista_metricas.pack(fill="both", expand=True)

        self.vista_csv = VistaLimpiadorCSV(self.tab_csv, callback_actualizar_kpis=None)
        self.vista_csv.pack(fill="both", expand=True)

        self.vista_config = VistaConfiguracion(self.tab_config)
        self.vista_config.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()