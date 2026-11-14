# views/limpiador_csv.py
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from database.conexion import obtener_conexion

class VistaLimpiadorCSV(ctk.CTkFrame):
    def __init__(self, parent, callback_actualizar_kpis):
        super().__init__(parent, fg_color="transparent")
        self.callback_actualizar_kpis = callback_actualizar_kpis
        
        self.crear_interfaz()

    def crear_interfaz(self):
        header_csv = ctk.CTkFrame(self, fg_color="transparent")
        header_csv.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(header_csv, text="🧹 Módulo de Limpieza e Ingesta de Registros CSV", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        btn_cargar = ctk.CTkButton(header_csv, text="📂 Seleccionar y Limpiar CSV", fg_color="#2563EB", hover_color="#1D4ED8", command=self.importar_y_limpiar_csv)
        btn_cargar.pack(side="right")

        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ctk.CTkLabel(preview_frame, text="Previsualización de Datos Limpios listos para BD", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)

        tabla_container = ctk.CTkFrame(preview_frame, fg_color="transparent")
        tabla_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columnas_csv = ("nombre", "fecha", "hora", "tipo")
        self.tabla_csv = ttk.Treeview(tabla_container, columns=columnas_csv, show="headings", height=15)
        self.tabla_csv.heading("nombre", text="Nombre / Docente")
        self.tabla_csv.heading("fecha", text="Fecha (YYYY-MM-DD)")
        self.tabla_csv.heading("hora", text="Hora (HH:MM:SS)")
        self.tabla_csv.heading("tipo", text="Tipo (Calculado)")

        self.tabla_csv.column("nombre", width=300)
        self.tabla_csv.column("fecha", width=150, anchor="center")
        self.tabla_csv.column("hora", width=150, anchor="center")
        self.tabla_csv.column("tipo", width=150, anchor="center")
        
        scroll_y = ttk.Scrollbar(tabla_container, orient="vertical", command=self.tabla_csv.yview)
        self.tabla_csv.configure(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side="right", fill="y")
        self.tabla_csv.pack(side="left", fill="both", expand=True)

    def _detectar_columna(self, columnas, palabras_clave):
        for col in columnas:
            col_str = str(col).lower()
            for palabra in palabras_clave:
                if palabra in col_str:
                    return col
        return None

    def importar_y_limpiar_csv(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
        if not archivo:
            return

        try:
            try:
                df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
                if len(df.columns) == 1:
                    df = pd.read_csv(archivo, sep=',', encoding='utf-8-sig', on_bad_lines='skip')
            except Exception:
                df = pd.read_csv(archivo, sep=';', encoding='latin1', on_bad_lines='skip')

            df.columns = [str(c).strip().lower() for c in df.columns]
            
            col_nombre = self._detectar_columna(df.columns, ['nome (usuário)', 'nombre', 'empleado', 'maestro', 'name'])
            col_fechahora = self._detectar_columna(df.columns, ['data e hora', 'fecha y hora'])
            
            if not col_nombre or not col_fechahora:
                messagebox.showerror("Error", "El archivo no tiene el formato biométrico esperado.")
                return

            df_sub = df[[col_fechahora, col_nombre]].copy()
            df_sub.columns = ["Fecha_Hora_Raw", "Nombre"]
            df_sub["Nombre"] = df_sub["Nombre"].astype(str).str.strip()
            
            df_sub = df_sub.dropna(subset=["Fecha_Hora_Raw", "Nombre"])
            df_sub = df_sub[~df_sub['Nombre'].isin(['nan', 'Desconocido', '', 'None'])]

            df_sub["Fecha_Hora"] = pd.to_datetime(df_sub["Fecha_Hora_Raw"].astype(str).str.strip(), format="%d/%m/%Y %H:%M:%S", errors="coerce")
            df_sub = df_sub.dropna(subset=["Fecha_Hora"])
            df_sub["Fecha_Texto"] = df_sub["Fecha_Hora"].dt.strftime("%Y-%m-%d")

            df_resumen = df_sub.groupby(["Nombre", "Fecha_Texto"], sort=False).agg(
                Entrada=("Fecha_Hora", lambda x: x.min().strftime("%H:%M:%S")),
                Salida=("Fecha_Hora", lambda x: x.max().strftime("%H:%M:%S"))
            ).reset_index()

            datos_limpios = []
            for _, row in df_resumen.iterrows():
                nombre = row["Nombre"]
                fecha = row["Fecha_Texto"]
                hora_entrada = row["Entrada"]
                hora_salida = row["Salida"]

                datos_limpios.append((nombre, fecha, hora_entrada, "ENTRADA"))
                if hora_entrada != hora_salida:
                    datos_limpios.append((nombre, fecha, hora_salida, "SALIDA"))

            for item in self.tabla_csv.get_children():
                self.tabla_csv.delete(item)

            for row in datos_limpios:
                self.tabla_csv.insert("", "end", values=row)

            # Guardar en Base de Datos de forma limpia
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            nuevos_inserciones = 0
            duplicados_omitidos = 0

            for nombre, fecha, hora, tipo in datos_limpios:
                # Buscar si el maestro ya existe por nombre exacto
                cursor.execute("SELECT id FROM maestros WHERE nombre = ?", (nombre,))
                res = cursor.fetchone()
                
                if res:
                    id_maestro = res[0]
                else:
                    # Crear nuevo maestro limpio (sin identificadores de texto complejos)
                    cursor.execute("INSERT INTO maestros (nombre, tipo, activo) VALUES (?, 'NORMAL', 1)", (nombre,))
                    id_maestro = cursor.lastrowid

                # Evitar ponchadas duplicadas
                cursor.execute("""
                    SELECT id FROM ponchadas 
                    WHERE idMaestro = ? AND fecha = ? AND hora = ? AND tipo = ?
                """, (id_maestro, fecha, hora, tipo))
                
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO ponchadas (idMaestro, fecha, hora, tipo) VALUES (?, ?, ?, ?)", 
                                   (id_maestro, fecha, hora, tipo))
                    nuevos_inserciones += 1
                else:
                    duplicados_omitidos += 1

            conn.commit()
            conn.close()

            messagebox.showinfo("Sincronización Completa", f"¡Proceso finalizado!\n\n• Nuevos registros: {nuevos_inserciones}\n• Duplicados omitidos: {duplicados_omitidos}")
            if self.callback_actualizar_kpis:
                self.callback_actualizar_kpis()

        except Exception as e:
            messagebox.showerror("Error de Ingesta", f"Ocurrió un error: {str(e)}")