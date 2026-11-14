# views/dashboard_kpis.py
import customtkinter as ctk
from tkinter import ttk
from database.conexion import obtener_conexion

class VentanaDirectorio(ctk.CTkToplevel):
    """Ventana modal segura y exclusiva para consultar el catálogo de nombres reales mediante el ID base."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📖 Directorio y Catálogo de Personal (Confidencial)")
        self.geometry("620x520")
        self.grab_set()
        
        self.crear_interfaz()
        self.cargar_directorio()

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(header, text="🔐 Catálogo de Identificación Interna", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        self.entry_buscar_modal = ctk.CTkEntry(header, placeholder_text="Buscar por nombre o ID...", width=220)
        self.entry_buscar_modal.pack(side="right", padx=5)
        self.entry_buscar_modal.bind("<KeyRelease>", self.cargar_directorio)

        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1E293B", foreground="white", fieldbackground="#1E293B", borderwidth=0, rowheight=26)
        style.configure("Treeview.Heading", background="#334155", foreground="white", font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#2563EB')])

        columnas = ("id", "docente_label", "nombre", "tipo")
        self.tabla_dir = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=15)
        
        self.tabla_dir.heading("id", text="ID Clave")
        self.tabla_dir.heading("docente_label", text="Identificador")
        self.tabla_dir.heading("nombre", text="Nombre Real del Docente")
        self.tabla_dir.heading("tipo", text="Tipo")

        self.tabla_dir.column("id", width=70, anchor="center")
        self.tabla_dir.column("docente_label", width=120, anchor="center")
        self.tabla_dir.column("nombre", width=280, anchor="w")
        self.tabla_dir.column("tipo", width=90, anchor="center")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_dir.yview)
        self.tabla_dir.configure(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side="right", fill="y")
        self.tabla_dir.pack(side="left", fill="both", expand=True)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(footer, text="⚠️ Uso exclusivo administrativo para trazabilidad de identidades.", text_color="#9CA3AF", font=ctk.CTkFont(size=11)).pack(side="left")

    def cargar_directorio(self, *args):
        filtro = self.entry_buscar_modal.get().strip()
        for item in self.tabla_dir.get_children():
            self.tabla_dir.delete(item)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            if filtro:
                cursor.execute("""
                    SELECT id, nombre, tipo 
                    FROM maestros 
                    WHERE nombre LIKE ? OR CAST(id AS TEXT) LIKE ?
                    ORDER BY id ASC
                """, (f"%{filtro}%", f"%{filtro}%"))
            else:
                cursor.execute("SELECT id, nombre, tipo FROM maestros ORDER BY id ASC")

            for row in cursor.fetchall():
                id_docente, nombre, tipo = row
                docente_label = f"Docente ID #{id_docente}"
                self.tabla_dir.insert("", "end", values=(id_docente, docente_label, nombre, tipo))

            conn.close()
        except Exception as e:
            print("Error cargando directorio:", e)


class VistaKPIs(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 10))

        ctk.CTkLabel(header_frame, text="Panel General de Asistencias", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        filtros_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filtros_frame.pack(side="right")

        self.btn_directorio = ctk.CTkButton(
            filtros_frame, text="📖 Directorio", fg_color="#4B5563", hover_color="#374151", width=100,
            command=self.abrir_modal_directorio
        )
        self.btn_directorio.pack(side="left", padx=5)

        ctk.CTkLabel(filtros_frame, text="Tipo:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(filtros_frame, values=["Todos", "NORMAL", "PA"], command=self.cargar_datos, width=110)
        self.combo_tipo.pack(side="left", padx=5)
        self.combo_tipo.set("Todos")

        ctk.CTkLabel(filtros_frame, text="Buscar:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.entry_busqueda = ctk.CTkEntry(filtros_frame, placeholder_text="ID o término...", width=140)
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", self.cargar_datos)

        self.btn_actualizar = ctk.CTkButton(filtros_frame, text="🔄 Recargar", width=90, command=self.limpiar_y_recargar)
        self.btn_actualizar.pack(side="left", padx=10)

        # Tarjetas de KPIs
        self.grid_kpis = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_kpis.pack(fill="x", padx=10, pady=5)
        self.grid_kpis.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_activos = self._crear_tarjeta(self.grid_kpis, "✅ Docentes Activos", "0", 0, 0, "#10B981")
        self.lbl_registros = self._crear_tarjeta(self.grid_kpis, "⏱️ Registros Totales", "0", 0, 1, "#38BDF8")
        self.lbl_retardos = self._crear_tarjeta(self.grid_kpis, "⚠️ Retardos Globales", "0", 0, 2, "#F59E0B")
        self.lbl_incompletos = self._crear_tarjeta(self.grid_kpis, "❌ Sin Salida", "0", 0, 3, "#EF4444")

        # Tabla Principal
        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header_tabla_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        header_tabla_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header_tabla_frame, text="Desempeño y Asistencias por Identificador Seguro", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        self.lbl_conteo_registros = ctk.CTkLabel(header_tabla_frame, text="Mostrando 0 registros", text_color="#9CA3AF", font=ctk.CTkFont(size=11))
        self.lbl_conteo_registros.pack(side="right")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1E293B", foreground="white", fieldbackground="#1E293B", borderwidth=0, rowheight=24)
        style.configure("Treeview.Heading", background="#334155", foreground="white", font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#2563EB')])

        columnas = ("id", "nombre", "tipo", "total_asistencias", "retardos")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=10)
        
        self.tabla.heading("id", text="ID Clave")
        self.tabla.heading("nombre", text="Identificador de Personal (Confidencial)")
        self.tabla.heading("tipo", text="Tipo")
        self.tabla.heading("total_asistencias", text="Total Entradas")
        self.tabla.heading("retardos", text="Retardos (> 08:10)")
        
        self.tabla.column("id", width=80, anchor="center")
        self.tabla.column("nombre", width=340, anchor="w")
        self.tabla.column("tipo", width=110, anchor="center")
        self.tabla.column("total_asistencias", width=130, anchor="center")
        self.tabla.column("retardos", width=130, anchor="center")
        
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_tarjeta(self, parent, titulo, valor_inicial, fila, columna, color):
        card = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=8)
        card.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(anchor="center", pady=(8, 0))
        lbl_valor = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=24, weight="bold"), text_color=color)
        lbl_valor.pack(anchor="center", pady=(0, 8))
        return lbl_valor

    def abrir_modal_directorio(self):
        VentanaDirectorio(self)

    def limpiar_y_recargar(self):
        self.entry_busqueda.delete(0, 'end')
        self.combo_tipo.set("Todos")
        self.cargar_datos()

    def cargar_datos(self, *args):
        texto_busqueda = self.entry_busqueda.get().strip()
        tipo_seleccionado = self.combo_tipo.get()
        
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            condiciones = ["m.activo = 1"]
            params = []

            if tipo_seleccionado != "Todos":
                condiciones.append("m.tipo = ?")
                params.append(tipo_seleccionado)

            if texto_busqueda:
                condiciones.append("(CAST(m.id AS TEXT) LIKE ? OR m.nombre LIKE ?)")
                params.extend([f"%{texto_busqueda}%", f"%{texto_busqueda}%"])

            where_clause = " WHERE " + " AND ".join(condiciones) if condiciones else ""

            cursor.execute(f"SELECT COUNT(*) FROM maestros m {where_clause}", params)
            self.lbl_activos.configure(text=str(cursor.fetchone()[0]))

            cursor.execute(f"SELECT COUNT(*) FROM ponchadas p JOIN maestros m ON p.idMaestro = m.id {where_clause}", params)
            self.lbl_registros.configure(text=str(cursor.fetchone()[0]))

            cursor.execute(f"SELECT COUNT(*) FROM ponchadas p JOIN maestros m ON p.idMaestro = m.id {where_clause} AND p.tipo = 'ENTRADA' AND p.hora > '08:10:00'", params)
            self.lbl_retardos.configure(text=str(cursor.fetchone()[0]))

            for item in self.tabla.get_children():
                self.tabla.delete(item)

            query_tabla = f"""
                SELECT m.id, m.tipo,
                       (SELECT COUNT(*) FROM ponchadas WHERE idMaestro = m.id AND tipo = 'ENTRADA') as asistencias,
                       (SELECT COUNT(*) FROM ponchadas WHERE idMaestro = m.id AND tipo = 'ENTRADA' AND hora > '08:10:00') as retardos
                FROM maestros m
                {where_clause}
                ORDER BY retardos DESC, m.id ASC
            """
            cursor.execute(query_tabla, params)
            filas = cursor.fetchall()
            
            for row in filas:
                id_docente, tipo_docente, asistencias, retardos = row
                nombre_anonimo = f"Docente ID #{id_docente}"
                self.tabla.insert("", "end", values=(id_docente, nombre_anonimo, tipo_docente, asistencias, retardos))

            self.lbl_conteo_registros.configure(text=f"Mostrando {len(filas)} registros")
            conn.close()
        except Exception as e:
            print("Error cargando KPIs:", e)