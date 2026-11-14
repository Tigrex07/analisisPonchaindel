# views/horarios.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import obtener_conexion

class VistaHorarios(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.id_maestro_seleccionado = None
        self.crear_interfaz()
        self.cargar_maestros()

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="⏰ Gestión y Asignación de Horarios por Docente", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        # Contenedor principal en dos columnas
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # --- PANEL IZQUIERDO: Lista de Docentes (width se pasa en el constructor) ---
        left_frame = ctk.CTkFrame(main_container, width=300)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Seleccione un Docente", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        self.entry_buscar_docente = ctk.CTkEntry(left_frame, placeholder_text="Buscar docente...")
        self.entry_buscar_docente.pack(fill="x", padx=10, pady=(0, 10))
        self.entry_buscar_docente.bind("<KeyRelease>", self.cargar_maestros)

        doc_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        doc_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tabla_docentes = ttk.Treeview(doc_container, columns=("id", "nombre"), show="headings", height=15)
        self.tabla_docentes.heading("id", text="ID")
        self.tabla_docentes.heading("nombre", text="Docente")
        self.tabla_docentes.column("id", width=60, anchor="center")
        self.tabla_docentes.column("nombre", width=200, anchor="w")

        scroll_doc = ttk.Scrollbar(doc_container, orient="vertical", command=self.tabla_docentes.yview)
        self.tabla_docentes.configure(yscrollcommand=scroll_doc.set)
        
        scroll_doc.pack(side="right", fill="y")
        self.tabla_docentes.pack(side="left", fill="both", expand=True)
        self.tabla_docentes.bind("<<TreeviewSelect>>", self.seleccionar_docente)

        # --- PANEL DERECHO: Horarios del Docente Seleccionado ---
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_titulo_horarios = ctk.CTkLabel(right_frame, text="Seleccione un docente para ver y asignar horarios", font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_titulo_horarios.pack(anchor="w", padx=15, pady=15)

        # Formulario para agregar horario
        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 15))

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

        self.btn_agregar_horario = ctk.CTkButton(form_frame, text="➕ Asignar", fg_color="#2563EB", hover_color="#1D4ED8", command=self.guardar_horario, state="disabled", width=110)
        self.btn_agregar_horario.grid(row=1, column=3, padx=15, pady=5)

        # Tabla de Horarios Asignados
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

    def seleccionar_docente(self, event):
        seleccion = self.tabla_docentes.selection()
        if not seleccion:
            return
        item = self.tabla_docentes.item(seleccion)
        self.id_maestro_seleccionado = item['values'][0]
        
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM maestros WHERE id = ?", (self.id_maestro_seleccionado,))
            res = cursor.fetchone()
            conn.close()
            
            if res:
                self.lbl_titulo_horarios.configure(text=f"Horarios para: Docente ID #{self.id_maestro_seleccionado}")
                self.btn_agregar_horario.configure(state="normal")
                self.cargar_horarios_docente()
        except Exception as e:
            print("Error seleccionando docente:", e)

    def cargar_horarios_docente(self):
        for item in self.tabla_horarios.get_children():
            self.tabla_horarios.delete(item)

        if not self.id_maestro_seleccionado:
            return

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
            """, (self.id_maestro_seleccionado,))
            for row in cursor.fetchall():
                self.tabla_horarios.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print("Error cargando horarios:", e)

    def guardar_horario(self):
        if not self.id_maestro_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un docente primero.")
            return

        dia = self.combo_dia.get()
        entrada = self.entry_entrada.get().strip() or "08:00:00"
        salida = self.entry_salida.get().strip() or "16:00:00"

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM horarios WHERE idMaestro = ? AND dia_semana = ?", (self.id_maestro_seleccionado, dia))
            existe = cursor.fetchone()

            if existe:
                cursor.execute("UPDATE horarios SET hora_entrada = ?, hora_salida = ? WHERE id = ?", (entrada, salida, existe[0]))
            else:
                cursor.execute("INSERT INTO horarios (idMaestro, dia_semana, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)", (self.id_maestro_seleccionado, dia, entrada, salida))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Horario para el día {dia} guardado correctamente.")
            self.cargar_horarios_docente()
            self.entry_entrada.delete(0, 'end')
            self.entry_salida.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el horario:\n{str(e)}")

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
                self.cargar_horarios_docente()
                messagebox.showinfo("Éxito", "Horario eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")