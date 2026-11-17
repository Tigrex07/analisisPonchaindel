# views/horarios.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import obtener_conexion
from views.dashboard_kpis import VentanaDirectorio

class VistaHorarios(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.ids_maestros_seleccionados = []
        self.crear_interfaz()
        self.cargar_maestros()

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(header, text="⏰ Gestión y Asignación Masiva de Horarios", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        # Botones de acción rápida en la cabecera (Directorio y Recargar)
        acciones_header = ctk.CTkFrame(header, fg_color="transparent")
        acciones_header.pack(side="right")

        self.btn_directorio = ctk.CTkButton(
            acciones_header, text="📖 Directorio", fg_color="#4B5563", hover_color="#374151", width=100,
            command=lambda: VentanaDirectorio(self)
        )
        self.btn_directorio.pack(side="left", padx=5)

        self.btn_recargar = ctk.CTkButton(
            acciones_header, text="🔄 Recargar", width=90, command=self.cargar_maestros
        )
        self.btn_recargar.pack(side="left", padx=5)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # --- PANEL IZQUIERDO: Lista de Docentes ---
        left_frame = ctk.CTkFrame(main_container, width=300)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Seleccione Docente(s) (Ctrl+Click)", font=ctk.CTkFont(weight="bold", size=11)).pack(anchor="w", padx=10, pady=10)
        
        self.entry_buscar_docente = ctk.CTkEntry(left_frame, placeholder_text="Buscar docente...")
        self.entry_buscar_docente.pack(fill="x", padx=10, pady=(0, 10))
        self.entry_buscar_docente.bind("<KeyRelease>", self.cargar_maestros)

        doc_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        doc_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tabla_docentes = ttk.Treeview(doc_container, columns=("id", "nombre"), show="headings", height=15, selectmode="extended")
        self.tabla_docentes.heading("id", text="ID")
        self.tabla_docentes.heading("nombre", text="Docente")
        self.tabla_docentes.column("id", width=60, anchor="center")
        self.tabla_docentes.column("nombre", width=200, anchor="w")

        scroll_doc = ttk.Scrollbar(doc_container, orient="vertical", command=self.tabla_docentes.yview)
        self.tabla_docentes.configure(yscrollcommand=scroll_doc.set)
        
        scroll_doc.pack(side="right", fill="y")
        self.tabla_docentes.pack(side="left", fill="both", expand=True)
        self.tabla_docentes.bind("<<TreeviewSelect>>", self.cambiar_seleccion_docentes)

        # --- PANEL DERECHO ---
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_titulo_horarios = ctk.CTkLabel(right_frame, text="Seleccione uno o varios docentes para asignar horarios", font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_titulo_horarios.pack(anchor="w", padx=15, pady=15)

        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Día:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_dia = ctk.CTkComboBox(form_frame, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], width=130)
        self.combo_dia.grid(row=1, column=0, padx=5, pady=5)
        self.combo_dia.set("Lunes")

        ctk.CTkLabel(form_frame, text="Entrada (HH:MM:SS):").grid(row=0, column=1, sticky="w", padx=5)
        self.entry_entrada = ctk.CTkEntry(form_frame, placeholder_text="08:00:00", width=130)
        self.entry_entrada.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Salida (HH:MM:SS):").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_salida = ctk.CTkEntry(form_frame, placeholder_text="16:00:00", width=130)
        self.entry_salida.grid(row=1, column=2, padx=5, pady=5)

        self.btn_agregar_horario = ctk.CTkButton(form_frame, text="➕ Asignar Día", fg_color="#2563EB", hover_color="#1D4ED8", command=self.guardar_horario, state="disabled", width=110)
        self.btn_agregar_horario.grid(row=1, column=3, padx=15, pady=5)

        quick_frame = ctk.CTkFrame(right_frame, fg_color="#1E293B", corner_radius=8)
        quick_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(quick_frame, text="⚡ Asignación Masiva Rápida (Aplica a los seleccionados):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(anchor="w", padx=12, pady=(8, 4))

        btns_sub_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        btns_sub_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.btn_lv = ctk.CTkButton(
            btns_sub_frame, text="📅 Lunes a Viernes", fg_color="#0D9488", hover_color="#0F766E",
            command=lambda: self.aplicar_a_rango(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]), state="disabled", width=190
        )
        self.btn_lv.pack(side="left", padx=(0, 10))

        self.btn_ls = ctk.CTkButton(
            btns_sub_frame, text="📅 Lunes a Sábado", fg_color="#0284C7", hover_color="#0369A1",
            command=lambda: self.aplicar_a_rango(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]), state="disabled", width=190
        )
        self.btn_ls.pack(side="left")

        tabla_hor_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        tabla_hor_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tabla_horarios = ttk.Treeview(tabla_hor_container, columns=("id", "dia", "entrada", "salida"), show="headings", height=10)
        self.tabla_horarios.heading("id", text="ID")
        self.tabla_horarios.heading("dia", text="Día de la Semana")
        self.tabla_horarios.heading("entrada", text="Hora Entrada")
        self.tabla_horarios.heading("salida", text="Hora Salida")

        self.tabla_horarios.column("id", width=60, anchor="center")
        self.tabla_horarios.column("dia", width=150, anchor="center")
        self.tabla_horarios.column("entrada", width=150, anchor="center")
        self.tabla_horarios.column("salida", width=150, anchor="center")

        scroll_hor = ttk.Scrollbar(tabla_hor_container, orient="vertical", command=self.tabla_horarios.yview)
        self.tabla_horarios.configure(yscrollcommand=scroll_hor.set)
        
        scroll_hor.pack(side="right", fill="y")
        self.tabla_horarios.pack(side="left", fill="both", expand=True)

        btn_eliminar = ctk.CTkButton(right_frame, text="🗑️ Eliminar Horario Seleccionado", fg_color="#DC2626", hover_color="#B91C1C", command=self.eliminar_horario)
        btn_eliminar.pack(anchor="e", padx=15, pady=(0, 15))

    def cargar_maestros(self, *args):
        filtro = self.entry_buscar_docente.get().strip()
        for item in self.tabla_docentes.get_children():
            self.tabla_docentes.delete(item)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            if filtro:
                cursor.execute("SELECT id, nombre FROM maestros WHERE nombre LIKE ? OR CAST(id AS TEXT) LIKE ? ORDER BY id ASC", (f"%{filtro}%", f"%{filtro}%"))
            else:
                cursor.execute("SELECT id, nombre FROM maestros ORDER BY id ASC")

            for row in cursor.fetchall():
                id_docente, nombre = row
                etiqueta = f"Docente ID #{id_docente}"
                self.tabla_docentes.insert("", "end", values=(id_docente, etiqueta))
            conn.close()
        except Exception as e:
            print("Error cargando maestros:", e)

    def cambiar_seleccion_docentes(self, event):
        selecciones = self.tabla_docentes.selection()
        if not selecciones:
            self.ids_maestros_seleccionados = []
            self.lbl_titulo_horarios.configure(text="Seleccione uno o varios docentes para asignar horarios")
            self.btn_agregar_horario.configure(state="disabled")
            self.btn_lv.configure(state="disabled")
            self.btn_ls.configure(state="disabled")
            for item in self.tabla_horarios.get_children():
                self.tabla_horarios.delete(item)
            return

        self.ids_maestros_seleccionados = [self.tabla_docentes.item(sel)['values'][0] for sel in selecciones]
        
        if len(self.ids_maestros_seleccionados) == 1:
            id_unico = self.ids_maestros_seleccionados[0]
            self.lbl_titulo_horarios.configure(text=f"Horarios para: Docente ID #{id_unico}")
            self.cargar_horarios_docente(id_unico)
        else:
            self.lbl_titulo_horarios.configure(text=f"⚡ Asignación Masiva a {len(self.ids_maestros_seleccionados)} docentes seleccionados")
            for item in self.tabla_horarios.get_children():
                self.tabla_horarios.delete(item)

        self.btn_agregar_horario.configure(state="normal")
        self.btn_lv.configure(state="normal")
        self.btn_ls.configure(state="normal")

    def cargar_horarios_docente(self, id_maestro):
        for item in self.tabla_horarios.get_children():
            self.tabla_horarios.delete(item)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, dia_semana, hora_entrada, hora_salida 
                FROM horarios 
                WHERE idMaestro = ? 
                ORDER BY CASE dia_semana 
                    WHEN 'Lunes' THEN 1 
                    WHEN 'Martes' THEN 2 
                    WHEN 'Miércoles' THEN 3 
                    WHEN 'Jueves' THEN 4 
                    WHEN 'Viernes' THEN 5 
                    WHEN 'Sábado' THEN 6 
                    ELSE 7 END
            """, (id_maestro,))
            for row in cursor.fetchall():
                self.tabla_horarios.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print("Error cargando horarios:", e)

    def guardar_horario(self):
        if not self.ids_maestros_seleccionados:
            messagebox.showwarning("Atención", "Seleccione al menos un docente.")
            return

        dia = self.combo_dia.get()
        entrada = self.entry_entrada.get().strip() or "08:00:00"
        salida = self.entry_salida.get().strip() or "16:00:00"

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            for id_maestro in self.ids_maestros_seleccionados:
                cursor.execute("SELECT id FROM horarios WHERE idMaestro = ? AND dia_semana = ?", (id_maestro, dia))
                existe = cursor.fetchone()

                if existe:
                    cursor.execute("UPDATE horarios SET hora_entrada = ?, hora_salida = ? WHERE id = ?", (entrada, salida, existe[0]))
                else:
                    cursor.execute("INSERT INTO horarios (idMaestro, dia_semana, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)", (id_maestro, dia, entrada, salida))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Horario para el día {dia} asignado a {len(self.ids_maestros_seleccionados)} docente(s).")
            if len(self.ids_maestros_seleccionados) == 1:
                self.cargar_horarios_docente(self.ids_maestros_seleccionados[0])
            self.entry_entrada.delete(0, 'end')
            self.entry_salida.delete(0, 'end')

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el horario:\n{str(e)}")

    def aplicar_a_rango(self, dias_rango):
        if not self.ids_maestros_seleccionados:
            messagebox.showwarning("Atención", "Seleccione al menos un docente.")
            return

        entrada = self.entry_entrada.get().strip() or "08:00:00"
        salida = self.entry_salida.get().strip() or "16:00:00"

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            for id_maestro in self.ids_maestros_seleccionados:
                for dia in dias_rango:
                    cursor.execute("SELECT id FROM horarios WHERE idMaestro = ? AND dia_semana = ?", (id_maestro, dia))
                    existe = cursor.fetchone()

                    if existe:
                        cursor.execute("UPDATE horarios SET hora_entrada = ?, hora_salida = ? WHERE id = ?", (entrada, salida, existe[0]))
                    else:
                        cursor.execute("INSERT INTO horarios (idMaestro, dia_semana, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)", (id_maestro, dia, entrada, salida))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Bloque de horarios aplicado correctamente a {len(self.ids_maestros_seleccionados)} docente(s).")
            if len(self.ids_maestros_seleccionados) == 1:
                self.cargar_horarios_docente(self.ids_maestros_seleccionados[0])
            self.entry_entrada.delete(0, 'end')
            self.entry_salida.delete(0, 'end')

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el bloque de horarios:\n{str(e)}")

    def eliminar_horario(self):
        seleccion = self.tabla_horarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un horario de la tabla para eliminar.")
            return

        item = self.tabla_horarios.item(seleccion)
        id_horario = item['values'][0]

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este horario?"):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM horarios WHERE id = ?", (id_horario,))
                conn.commit()
                conn.close()
                if len(self.ids_maestros_seleccionados) == 1:
                    self.cargar_horarios_docente(self.ids_maestros_seleccionados[0])
                messagebox.showinfo("Éxito", "Horario eliminado correctamente.")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")