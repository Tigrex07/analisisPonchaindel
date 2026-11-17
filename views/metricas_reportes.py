# views/metricas_reportes.py
import customtkinter as ctk

class VistaMetricasReportes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_interfaz()

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="📈 Métricas Avanzadas y Reportes Institucionales", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ctk.CTkLabel(
            body, 
            text="Panel en construcción (Próximo paso):\nAquí mostraremos incidencias de ponchada única, retardos mensuales por gráfica y los botones de exportación a Excel (Sindicalizados y por Áreas UTN).", 
            font=ctk.CTkFont(size=14), 
            text_color="#9CA3AF"
        ).pack(expand=True)