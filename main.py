import customtkinter as ctk

from views import VistaKPIs, VistaLimpiadorCSV, VistaHorarios

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integral de RRHH - Control y Analíticas")
        self.geometry("1150x720")
        
        # Contenedor principal de Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear las pestañas de la interfaz
        self.tab_kpis = self.tabview.add("📊 Dashboard KPIs")
        self.tab_csv = self.tabview.add("📁 Limpiador e Importador CSV")
        self.tab_horarios = self.tabview.add("⏰ Gestión de Horarios")

        # Inicializar y empaquetar vistas
        self.vista_kpis = VistaKPIs(self.tab_kpis)
        self.vista_kpis.pack(fill="both", expand=True)

        self.vista_csv = VistaLimpiadorCSV(self.tab_csv, callback_actualizar_kpis=self.vista_kpis.cargar_datos)
        self.vista_csv.pack(fill="both", expand=True)

        self.vista_horarios = VistaHorarios(self.tab_horarios)
        self.vista_horarios.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()