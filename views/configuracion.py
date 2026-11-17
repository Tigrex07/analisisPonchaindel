# views/configuracion.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import obtener_conexion
from views.horarios import VistaHorarios

AREAS_UTN = [
    "Mecatrónica",
    "Operaciones Comerciales",
    "Tecnologías de la Información",
    "Procesos Industriales",
    "Energías Renovables"
]

class VistaConfiguracion(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_interfaz()

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="⚙️ Centro de Configuración y Administración", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        # Sub-pestañas dentro de Configuración
        self.config_tabs = ctk.CTkTabview(self)
        self.config_tabs.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_areas = self.config_tabs.add("👥 Áreas y Sindicalización")
        self.tab_horarios = self.config_tabs.add("⏰ Gestión de Horarios")
        self.tab_listas = self.config_tabs.add("📋 Listas Personalizadas")

        self.inicializar_subtab_areas()
        self.inicializar_subtab_horarios()
        self.inicializar_subtab_listas()

    # ================= SUB-TAB 1: ÁREAS Y SINDICALIZACIÓN =================
    def inicializar_subtab_areas(self):
        frame = self.tab_areas
        
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        # Buscador superior para áreas y sindicalización
        self.entry_buscar_areas = ctk.CTkEntry(top_frame, placeholder_text="Buscar docente por nombre o ID...", width=300)
        self.entry_buscar_areas.pack(side="left", padx=(0, 10))
        self.entry_buscar_areas.bind("<KeyRelease>", self.cargar_tabla_maestros_cfg)

        self.btn_guardar_areas = ctk.CTkButton(top_frame, text="💾 Guardar Cambios en Selección", fg_color="#2563EB", hover_color="#1D4ED8", command=self.guardar_cambios_maestro)
        self.btn_guardar_areas.pack(side="right")

        main_cont = ctk.CTkFrame(frame, fg_color="transparent")
        main_cont.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tabla maestros (usando nombres reales)
        tabla_frame = ctk.CTkFrame(main_cont)
        tabla_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columnas = ("id", "nombre", "area", "sindicalizado")
        self.tabla_maestros_cfg = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=14, selectmode="extended")
        self.tabla_maestros_cfg.heading("id", text="ID")
        self.tabla_maestros_cfg.heading("nombre", text="Nombre Real del Docente")
        self.tabla_maestros_cfg.heading("area", text="Área UTN")
        self.tabla_maestros_cfg.heading("sindicalizado", text="Sindicalizado")

        self.tabla_maestros_cfg.column("id", width=60, anchor="center")
        self.tabla_maestros_cfg.column("nombre", width=280, anchor="w")
        self.tabla_maestros_cfg.column("area", width=200, anchor="center")
        self.tabla_maestros_cfg.column("sindicalizado", width=100, anchor="center")

        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_maestros_cfg.yview)
        self.tabla_maestros_cfg.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla_maestros_cfg.pack(side="left", fill="both", expand=True)

        # Panel derecho: Edición rápida
        edit_frame = ctk.CTkFrame(main_cont, width=280)
        edit_frame.pack(side="right", fill="both", expand=False)
        edit_frame.pack_propagate(False)

        ctk.CTkLabel(edit_frame, text="Edición Rápida", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=15, pady=15)

        ctk.CTkLabel(edit_frame, text="Área Académica:").pack(anchor="w", padx=15, pady=(5, 0))
        self.combo_area_edit = ctk.CTkComboBox(edit_frame, values=AREAS_UTN, width=240)
        self.combo_area_edit.pack(anchor="w", padx=15, pady=(5, 15))

        ctk.CTkLabel(edit_frame, text="¿Es Sindicalizado?:").pack(anchor="w", padx=15, pady=(5, 0))
        self.combo_sind_edit = ctk.CTkComboBox(edit_frame, values=["Sí (Sindicalizado)", "No (Confianza/Externo)"], width=240)
        self.combo_sind_edit.pack(anchor="w", padx=15, pady=(5, 20))

        self.cargar_tabla_maestros_cfg()

    def cargar_tabla_maestros_cfg(self, *args):
        filtro = self.entry_buscar_areas.get().strip() if hasattr(self, 'entry_buscar_areas') else ""
        for item in self.tabla_maestros_cfg.get_children():
            self.tabla_maestros_cfg.delete(item)
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            if filtro:
                cursor.execute("""
                    SELECT id, nombre, area, sindicalizado 
                    FROM maestros 
                    WHERE nombre LIKE ? OR CAST(id AS TEXT) LIKE ?
                    ORDER BY id ASC
                """, (f"%{filtro}%", f"%{filtro}%"))
            else:
                cursor.execute("SELECT id, nombre, area, sindicalizado FROM maestros ORDER BY id ASC")

            for row in cursor.fetchall():
                id_m, nombre, area, sind = row
                sind_txt = "Sí" if sind == 1 else "No"
                self.tabla_maestros_cfg.insert("", "end", values=(id_m, nombre, area or "Sin Área", sind_txt))
            conn.close()
        except Exception as e:
            print("Error cargando config maestros:", e)

    def guardar_cambios_maestro(self):
        sels = self.tabla_maestros_cfg.selection()
        if not sels:
            messagebox.showwarning("Atención", "Seleccione al menos un docente en la tabla.")
            return

        nueva_area = self.combo_area_edit.get()
        sind_val = 1 if "Sí" in self.combo_sind_edit.get() else 0

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            for sel in sels:
                id_m = self.tabla_maestros_cfg.item(sel)['values'][0]
                cursor.execute("UPDATE maestros SET area = ?, sindicalizado = ? WHERE id = ?", (nueva_area, sind_val, id_m))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"Actualización aplicada a {len(sels)} docente(s).")
            self.cargar_tabla_maestros_cfg()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")

    # ================= SUB-TAB 2: GESTIÓN DE HORARIOS =================
    def inicializar_subtab_horarios(self):
        self.vista_horarios_inner = VistaHorarios(self.tab_horarios)
        self.vista_horarios_inner.pack(fill="both", expand=True)

    # ================= SUB-TAB 3: LISTAS PERSONALIZADAS =================
    def inicializar_subtab_listas(self):
        frame = self.tab_listas
        
        main_cont = ctk.CTkFrame(frame, fg_color="transparent")
        main_cont.pack(fill="both", expand=True, padx=10, pady=10)

        # Izquierda: Listas creadas
        left_f = ctk.CTkFrame(main_cont, width=280)
        left_f.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_f.pack_propagate(False)

        ctk.CTkLabel(left_f, text="Listas Personalizadas", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        self.entry_nueva_lista = ctk.CTkEntry(left_f, placeholder_text="Nombre de nueva lista...")
        self.entry_nueva_lista.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkButton(left_f, text="➕ Crear Lista", fg_color="#2563EB", hover_color="#1D4ED8", command=self.crear_lista_personalizada).pack(fill="x", padx=10, pady=(0, 10))

        self.tabla_listas = ttk.Treeview(left_f, columns=("id", "nombre"), show="headings", height=12)
        self.tabla_listas.heading("id", text="ID")
        self.tabla_listas.heading("nombre", text="Lista")
        self.tabla_listas.column("id", width=40, anchor="center")
        self.tabla_listas.column("nombre", width=200, anchor="w")
        self.tabla_listas.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabla_listas.bind("<<TreeviewSelect>>", self.cargar_miembros_lista)

        # Derecha: Integrantes con buscapersonas en ambos lados
        right_f = ctk.CTkFrame(main_cont)
        right_f.pack(side="right", fill="both", expand=True)

        self.lbl_titulo_lista_sel = ctk.CTkLabel(right_f, text="Seleccione una lista para administrar sus integrantes", font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_titulo_lista_sel.pack(anchor="w", padx=15, pady=15)

        miembros_cont = ctk.CTkFrame(right_f, fg_color="transparent")
        miembros_cont.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Columna Izquierda (Miembros actuales)
        miembros_sub = ctk.CTkFrame(miembros_cont)
        miembros_sub.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(miembros_sub, text="Docentes en esta Lista:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.entry_buscar_miembros = ctk.CTkEntry(miembros_sub, placeholder_text="Filtrar miembros...")
        self.entry_buscar_miembros.pack(fill="x", padx=10, pady=(0, 5))
        self.entry_buscar_miembros.bind("<KeyRelease>", self.cargar_miembros_lista)

        self.tabla_miembros = ttk.Treeview(miembros_sub, columns=("id", "nombre"), show="headings", height=9)
        self.tabla_miembros.heading("id", text="ID")
        self.tabla_miembros.heading("nombre", text="Nombre del Docente")
        self.tabla_miembros.column("id", width=50, anchor="center")
        self.tabla_miembros.column("nombre", width=200, anchor="w")
        self.tabla_miembros.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(miembros_sub, text="🗑️ Quitar de la Lista", fg_color="#DC2626", hover_color="#B91C1C", command=self.quitar_docente_lista).pack(anchor="e", padx=10, pady=5)

        # Columna Derecha (Docentes disponibles)
        disp_sub = ctk.CTkFrame(miembros_cont)
        disp_sub.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(disp_sub, text="Docentes Disponibles:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.entry_buscar_disponibles = ctk.CTkEntry(disp_sub, placeholder_text="Filtrar disponibles...")
        self.entry_buscar_disponibles.pack(fill="x", padx=10, pady=(0, 5))
        self.entry_buscar_disponibles.bind("<KeyRelease>", self.cargar_miembros_lista)

        self.tabla_disponibles = ttk.Treeview(disp_sub, columns=("id", "nombre"), show="headings", height=9, selectmode="extended")
        self.tabla_disponibles.heading("id", text="ID")
        self.tabla_disponibles.heading("nombre", text="Nombre del Docente")
        self.tabla_disponibles.column("id", width=50, anchor="center")
        self.tabla_disponibles.column("nombre", width=200, anchor="w")
        self.tabla_disponibles.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(disp_sub, text="➕ Agregar Seleccionados", fg_color="#10B981", hover_color="#059669", command=self.agregar_docentes_lista).pack(anchor="e", padx=10, pady=5)

        self.lista_seleccionada_id = None
        self.cargar_listas_personalizadas()

    def cargar_listas_personalizadas(self):
        for item in self.tabla_listas.get_children():
            self.tabla_listas.delete(item)
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM listas_personalizadas ORDER BY id ASC")
            for row in cursor.fetchall():
                self.tabla_listas.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print("Error cargando listas:", e)

    def crear_lista_personalizada(self):
        nombre = self.entry_nueva_lista.get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "Ingrese un nombre para la lista.")
            return
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO listas_personalizadas (nombre) VALUES (?)", (nombre,))
            conn.commit()
            conn.close()
            self.entry_nueva_lista.delete(0, 'end')
            self.cargar_listas_personalizadas()
            messagebox.showinfo("Éxito", f"Lista '{nombre}' creada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la lista (puede que ya exista):\n{str(e)}")

    def cargar_miembros_lista(self, event):
        sel = self.tabla_listas.selection()
        if not sel:
            return
        item = self.tabla_listas.item(sel[0])
        self.lista_seleccionada_id, nombre_lista = item['values']
        self.lbl_titulo_lista_sel.configure(text=f"Integrantes de la Lista: {nombre_lista}")

        filtro_miembros = self.entry_buscar_miembros.get().strip() if hasattr(self, 'entry_buscar_miembros') else ""
        filtro_disp = self.entry_buscar_disponibles.get().strip() if hasattr(self, 'entry_buscar_disponibles') else ""

        for item in self.tabla_miembros.get_children():
            self.tabla_miembros.delete(item)
        for item in self.tabla_disponibles.get_children():
            self.tabla_disponibles.delete(item)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            # Miembros filtrados por búsqueda
            query_m = """
                SELECT m.id, m.nombre FROM maestros m
                JOIN detalle_lista_maestros d ON m.id = d.id_maestro
                WHERE d.id_lista = ?
            """
            params_m = [self.lista_seleccionada_id]
            if filtro_miembros:
                query_m += " AND (m.nombre LIKE ? OR CAST(m.id AS TEXT) LIKE ?)"
                params_m.extend([f"%{filtro_miembros}%", f"%{filtro_miembros}%"])
            query_m += " ORDER BY m.id ASC"

            cursor.execute(query_m, params_m)
            for row in cursor.fetchall():
                self.tabla_miembros.insert("", "end", values=(row[0], row[1]))

            # Disponibles filtrados por búsqueda
            query_d = """
                SELECT id, nombre FROM maestros
                WHERE id NOT IN (SELECT id_maestro FROM detalle_lista_maestros WHERE id_lista = ?)
            """
            params_d = [self.lista_seleccionada_id]
            if filtro_disp:
                query_d += " AND (nombre LIKE ? OR CAST(id AS TEXT) LIKE ?)"
                params_d.extend([f"%{filtro_disp}%", f"%{filtro_disp}%"])
            query_d += " ORDER BY id ASC"

            cursor.execute(query_d, params_d)
            for row in cursor.fetchall():
                self.tabla_disponibles.insert("", "end", values=(row[0], row[1]))

            conn.close()
        except Exception as e:
            print("Error cargando miembros:", e)

    def agregar_docentes_lista(self):
        if not self.lista_seleccionada_id:
            messagebox.showwarning("Atención", "Seleccione una lista primero.")
            return
        sels = self.tabla_disponibles.selection()
        if not sels:
            messagebox.showwarning("Atención", "Seleccione al menos un docente disponible.")
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            for sel in sels:
                id_m = self.tabla_disponibles.item(sel)['values'][0]
                cursor.execute("INSERT OR IGNORE INTO detalle_lista_maestros (id_lista, id_maestro) VALUES (?, ?)", (self.lista_seleccionada_id, id_m))
            conn.commit()
            conn.close()
            self.cargar_miembros_lista(None)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron agregar:\n{str(e)}")

    def quitar_docente_lista(self):
        if not self.lista_seleccionada_id:
            return
        sel = self.tabla_miembros.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un docente de la lista para quitar.")
            return
        id_m = self.tabla_miembros.item(sel[0])['values'][0]

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM detalle_lista_maestros WHERE id_lista = ? AND id_maestro = ?", (self.lista_seleccionada_id, id_m))
            conn.commit()
            conn.close()
            self.cargar_miembros_lista(None)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo quitar:\n{str(e)}")