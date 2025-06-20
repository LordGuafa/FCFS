import tkinter as tk
from tkinter import ttk, messagebox
from model.proceso import Proceso
from typing import Callable, List, Optional, Any
from view.gantt import GanttChart

class ProcesoTableView(tk.Frame):
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        procesos: Optional[List[Proceso]] = None,
        on_edit: Optional[Callable[[int, str, Any], None]] = None,
        on_add: Optional[Callable[[], None]] = None,
        on_run: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        on_speed_change: Optional[Callable[[float], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        on_add_fcfs: Optional[Callable[[], None]] = None,           # <-- Nuevo
        on_add_prioridad: Optional[Callable[[], None]] = None       # <-- Nuevo
    ) -> None:
        super().__init__(master, bg="#1e1e2e")
        self.master: Optional[tk.Misc] = master #type: ignore
        self.procesos: List[Proceso] = procesos if procesos is not None else []
        self.on_edit: Optional[Callable[[int, str, Any], None]] = on_edit
        self.on_add: Callable[[], None] | None = on_add
        self.on_run: Callable[[], None] | None = on_run
        self.on_pause: Callable[[], None] | None = on_pause
        self.on_stop: Callable[[], None] | None = on_stop
        self.on_speed_change: Callable[[float], None] | None = on_speed_change
        self.on_reset: Callable[[], None] | None = on_reset
        self.on_add_fcfs: Callable[[], None] | None = on_add_fcfs
        self.on_add_prioridad: Callable[[], None] | None = on_add_prioridad
        
        # Variables de estado
        self.ejecutando = False
        self.pausado = False
        self.tiempo_simulacion = 0
        
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self) -> None:
        # Configurar estilo
        self.configure_styles()
        
        # Header con título y controles principales
        self.create_header()
        
        # Panel de control de simulación
        self.create_simulation_controls()
        
        # Tabla de procesos
        self.create_process_table()
        
        # Panel de información en tiempo real
        self.create_info_panel()
        
        # Diagrama de Gantt mejorado
        self.create_gantt_section()
        
        # Log de eventos
        self.create_log_section()

    def configure_styles(self) -> None:
        """Configura los estilos personalizados para la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores principales
        bg_primary = "#1e1e2e"
        bg_secondary = "#313244"
        accent_color = "#89b4fa"
        text_color = "#cdd6f4"
        success_color = "#a6e3a1"
        warning_color = "#f9e2af"
        error_color = "#f38ba8"
        
        # Configurar Treeview
        style.configure("Custom.Treeview",
                       background=bg_secondary,
                       fieldbackground=bg_secondary,
                       foreground=text_color,
                       borderwidth=0,
                       rowheight=32,
                       font=("Segoe UI", 10))
        
        style.configure("Custom.Treeview.Heading",
                       background=bg_primary,
                       foreground=text_color,
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=1,
                       relief="flat")
        
        # Configurar botones
        style.configure("Primary.TButton",
                       background=accent_color,
                       foreground="#1e1e2e",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0,
                       focuscolor="none")
        
        style.configure("Success.TButton",
                       background=success_color,
                       foreground="#1e1e2e",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0)
        
        style.configure("Warning.TButton",
                       background=warning_color,
                       foreground="#1e1e2e",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0)
        
        style.configure("Error.TButton",
                       background=error_color,
                       foreground="#1e1e2e",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0)

    def create_header(self) -> None:
        """Crea el header con título y información general"""
        header_frame = tk.Frame(self, bg="#1e1e2e", height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(
            header_frame,
            text="🔄 Simulador de Planificación de Procesos",
            font=("Segoe UI", 18, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e"
        )
        title_label.pack(side="left", anchor="w")
        
        # Información de estado
        self.status_frame = tk.Frame(header_frame, bg="#1e1e2e")
        self.status_frame.pack(side="right", anchor="e")
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Estado: Detenido",
            font=("Segoe UI", 12, "bold"),
            fg="#f38ba8",
            bg="#1e1e2e"
        )
        self.status_label.pack(anchor="e")
        
        self.time_label = tk.Label(
            self.status_frame,
            text="Tiempo: 0",
            font=("Segoe UI", 11),
            fg="#cdd6f4",
            bg="#1e1e2e"
        )
        self.time_label.pack(anchor="e")

    def create_simulation_controls(self) -> None:
        """Crea los controles de simulación"""
        control_frame = tk.Frame(self, bg="#313244", relief="flat", bd=1)
        control_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Frame interno con padding
        inner_frame = tk.Frame(control_frame, bg="#313244")
        inner_frame.pack(fill="x", padx=15, pady=15)
        
        # Botones de control
        buttons_frame = tk.Frame(inner_frame, bg="#313244")
        buttons_frame.pack(side="left")
        
        self.btn_run = ttk.Button(
            buttons_frame,
            text="▶ Ejecutar",
            style="Success.TButton",
            command=self.on_run_clicked
        )
        self.btn_run.pack(side="left", padx=(0, 5))
        
        self.btn_pause = ttk.Button(
            buttons_frame,
            text="⏸ Pausar",
            style="Warning.TButton",
            command=self.on_pause_clicked,
            state="disabled"
        )
        self.btn_pause.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(
            buttons_frame,
            text="⏹ Detener",
            style="Error.TButton",
            command=self.on_stop_clicked,
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)

        # Botón de reinicio
        self.btn_reset = ttk.Button(
            buttons_frame,
            text="🔄 Reiniciar",
            style="Primary.TButton",
            command=self.on_reset_clicked
        )
        self.btn_reset.pack(side="left", padx=5)
        
        # Control de velocidad
        speed_frame = tk.Frame(inner_frame, bg="#313244")
        speed_frame.pack(side="right")
        
        tk.Label(
            speed_frame,
            text="Velocidad:",
            font=("Segoe UI", 10),
            fg="#cdd6f4",
            bg="#313244"
        ).pack(side="left", padx=(0, 5))
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=0.1,
            to=3.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.speed_var,
            command=self.on_speed_changed,
            bg="#313244",
            fg="#cdd6f4",
            highlightbackground="#313244",
            troughcolor="#1e1e2e",
            activebackground="#89b4fa"
        )
        self.speed_scale.pack(side="left", padx=5)
        
        self.speed_label = tk.Label(
            speed_frame,
            text="1.0x",
            font=("Segoe UI", 10),
            fg="#cdd6f4",
            bg="#313244",
            width=5
        )
        self.speed_label.pack(side="left", padx=(5, 0))

    def create_process_table(self) -> None:
        """Crea la tabla de procesos mejorada"""
        table_frame = tk.LabelFrame(
            self,
            text=" 📋 Tabla de Procesos ",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            bd=1,
            relief="flat"
        )
        table_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botones para agregar procesos
        add_btn_frame = tk.Frame(table_frame, bg="#1e1e2e")
        add_btn_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ttk.Button(
            add_btn_frame,
            text="➕ Agregar FCFS",
            style="Primary.TButton",
            command=self.on_add_fcfs_clicked # type: ignore
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            add_btn_frame,
            text="➕ Agregar Prioridad",
            style="Primary.TButton",
            command=self.on_add_prioridad_clicked # type: ignore
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            add_btn_frame,
            text="➕ Agregar Proceso",
            style="Primary.TButton",
            command=self.on_add_clicked
        ).pack(side="left", padx=(0, 5))

        # Frame para la tabla con scrollbar
        table_container = tk.Frame(table_frame, bg="#1e1e2e")
        table_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configurar tabla
        columns = ("nombre", "tiempo_llegada", "rafaga", "prioridad", "algoritmo", 
                  "tiempo_inicio", "tiempo_final", "tiempo_retorno", "tiempo_espera")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            height=8
        )
        
        # Configurar columnas
        column_widths = {
            "nombre": 80,
            "tiempo_llegada": 100,
            "rafaga": 80,
            "prioridad": 80,
            "algoritmo": 100,
            "tiempo_inicio": 100,
            "tiempo_final": 100,
            "tiempo_retorno": 110,
            "tiempo_espera": 110
        }
        
        column_names = {
            "nombre": "Proceso",
            "tiempo_llegada": "T. Llegada",
            "rafaga": "Ráfaga",
            "prioridad": "Prioridad",
            "algoritmo": "Algoritmo",
            "tiempo_inicio": "T. Inicio",
            "tiempo_final": "T. Final",
            "tiempo_retorno": "T. Retorno",
            "tiempo_espera": "T. Espera"
        }
        
        for col in columns:
            self.tree.heading(col, text=column_names[col])
            self.tree.column(col, width=column_widths[col], anchor="center")
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # Menú contextual
        
        # Poblar tabla inicial
        self.refresh_table()

    def create_info_panel(self) -> None:
        """Crea el panel de información en tiempo real"""
        info_frame = tk.LabelFrame(
            self,
            text=" 📊 Información en Tiempo Real ",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            bd=1,
            relief="flat"
        )
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Grid de información
        stats_frame = tk.Frame(info_frame, bg="#1e1e2e")
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Métricas
        self.metrics = {}
        metrics_labels = [
            ("total_procesos", "Total de Procesos"),
            ("procesos_completados", "Completados"),
            ("procesos_ejecutando", "En Ejecución"),
            ("procesos_pendientes", "Pendientes"),
            ("tiempo_promedio_espera", "T. Espera Promedio"),
            ("tiempo_promedio_retorno", "T. Retorno Promedio")
        ]
        
        for i, (key, label) in enumerate(metrics_labels):
            row = i // 3
            col = i % 3
            
            metric_frame = tk.Frame(stats_frame, bg="#313244", relief="flat", bd=1)
            metric_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            stats_frame.grid_columnconfigure(col, weight=1)
            
            tk.Label(
                metric_frame,
                text=label,
                font=("Segoe UI", 9),
                fg="#a6adc8",
                bg="#313244"
            ).pack(pady=(5, 0))
            
            self.metrics[key] = tk.Label(
                metric_frame,
                text="0",
                font=("Segoe UI", 14, "bold"),
                fg="#cdd6f4",
                bg="#313244"
            )
            self.metrics[key].pack(pady=(0, 5))

    def create_gantt_section(self) -> None:
        """Crea la sección del diagrama de Gantt"""
        gantt_frame = tk.LabelFrame(
            self,
            text=" 📈 Diagrama de Gantt ",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            bd=1,
            relief="flat"
        )
        gantt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.gantt = GanttChart(gantt_frame, self.procesos)
        self.gantt.pack(fill="both", expand=True, padx=10, pady=10)

    def create_log_section(self) -> None:
        """Crea la sección de log de eventos"""
        log_frame = tk.LabelFrame(
            self,
            text=" 📝 Log de Eventos ",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            bd=1,
            relief="flat"
        )
        log_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Frame para el texto y scrollbar
        text_frame = tk.Frame(log_frame, bg="#1e1e2e")
        text_frame.pack(fill="x", padx=10, pady=10)
        
        self.log_text = tk.Text(
            text_frame,
            height=6,
            bg="#313244",
            fg="#cdd6f4",
            font=("JetBrains Mono", 9),
            state="disabled",
            borderwidth=0,
            insertbackground="#cdd6f4",
            selectbackground="#89b4fa",
            selectforeground="#1e1e2e"
        )
        
        log_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

    # Métodos de callback
    def on_run_clicked(self) -> None:
        """Maneja el clic en ejecutar"""
        if self.on_run:
            self.on_run()
        self.update_control_buttons(True, False)
        self.add_log_entry("🟢 Simulación iniciada")

    def on_pause_clicked(self) -> None:
        """Maneja el clic en pausar/reanudar"""
        if self.on_pause:
            self.on_pause()
        self.pausado = not self.pausado
        self.btn_pause.configure(text="⏵ Reanudar" if self.pausado else "⏸ Pausar")
        action = "pausada" if self.pausado else "reanudada"
        self.add_log_entry(f"🟡 Simulación {action}")

    def on_stop_clicked(self) -> None:
        """Maneja el clic en detener"""
        if self.on_stop:
            self.on_stop()
        self.update_control_buttons(False, True)
        self.pausado = False
        self.btn_pause.configure(text="⏸ Pausar")
        self.add_log_entry("🔴 Simulación detenida")

    def on_add_clicked(self) -> None:
        """Maneja el clic en agregar proceso"""
        if self.on_add:
            self.on_add()
        self.add_log_entry(f"➕ Nuevo proceso agregado")

    def on_reset_clicked(self) -> None:
        """Maneja el clic en reiniciar"""
        if self.on_reset:
            self.on_reset()
        self.add_log_entry("🔄 Simulación reiniciada")

    def on_speed_changed(self, value: str) -> None:
        """Maneja el cambio de velocidad"""
        speed = float(value)
        self.speed_label.configure(text=f"{speed:.1f}x")
        if self.on_speed_change:
            self.on_speed_change(speed)

    def update_control_buttons(self, running: bool, stopped: bool) -> None:
        """Actualiza el estado de los botones de control"""
        self.ejecutando = running
        if running:
            self.btn_run.configure(state="disabled")
            self.btn_pause.configure(state="normal")
            self.btn_stop.configure(state="normal")
            self.status_label.configure(text="Estado: Ejecutando", fg="#a6e3a1")
        elif stopped:
            self.btn_run.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
            self.status_label.configure(text="Estado: Detenido", fg="#f38ba8")

    def actualizar_tiempo_simulacion(self, tiempo: int) -> None:
        """Actualiza el tiempo de simulación en la interfaz"""
        self.tiempo_simulacion = tiempo
        self.time_label.configure(text=f"Tiempo: {tiempo}")
        self.update_metrics()
        if hasattr(self.gantt, 'actualizar_tiempo'):
            self.gantt.actualizar_tiempo(tiempo)

    def update_metrics(self) -> None:
        """Actualiza las métricas en tiempo real"""
        total = len(self.procesos)
        completados = len([p for p in self.procesos if p.tiempo_final > 0 and p.tiempo_final <= self.tiempo_simulacion])
        ejecutando = len([p for p in self.procesos if p.tiempo_inicio <= self.tiempo_simulacion < p.tiempo_final])
        pendientes = total - completados - ejecutando
        
        # Calcular promedios
        procesos_con_datos = [p for p in self.procesos if p.tiempo_espera > 0]
        promedio_espera = sum(p.tiempo_espera for p in procesos_con_datos) / len(procesos_con_datos) if procesos_con_datos else 0
        promedio_retorno = sum(p.tiempo_retorno for p in procesos_con_datos) / len(procesos_con_datos) if procesos_con_datos else 0
        
        # Actualizar labels
        self.metrics["total_procesos"].configure(text=str(total))
        self.metrics["procesos_completados"].configure(text=str(completados))
        self.metrics["procesos_ejecutando"].configure(text=str(ejecutando))
        self.metrics["procesos_pendientes"].configure(text=str(pendientes))
        self.metrics["tiempo_promedio_espera"].configure(text=f"{promedio_espera:.1f}")
        self.metrics["tiempo_promedio_retorno"].configure(text=f"{promedio_retorno:.1f}")

    def add_log_entry(self, message: str) -> None:
        """Agrega una entrada al log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def on_right_click(self, event: Any) -> None:
        """Maneja clic derecho para menú contextual"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.show_context_menu(event, item)

    def show_context_menu(self, event: Any, item: str) -> None:
        """Muestra menú contextual"""
        context_menu = tk.Menu(self, tearoff=0, bg="#313244", fg="#cdd6f4")
        context_menu.add_command(
            label="🗑️ Eliminar Proceso",
            command=lambda: self.delete_process(int(item))
        )
        context_menu.add_command(
            label="📝 Editar Proceso",
            command=lambda: self.edit_process(int(item))
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def delete_process(self, idx: int) -> None:
        """Elimina un proceso"""
        if messagebox.askyesno("Confirmar", "¿Eliminar este proceso?"):
            if 0 <= idx < len(self.procesos):
                process_name = self.procesos[idx].nombre
                del self.procesos[idx]
                self.refresh_table()
                self.add_log_entry(f"🗑️ Proceso {process_name} eliminado")

    def edit_process(self, idx: int) -> None:
        """Abre diálogo para editar proceso"""
        if 0 <= idx < len(self.procesos):
            self.show_edit_dialog(idx)

    def show_edit_dialog(self, idx: int) -> None:
        """Muestra diálogo de edición"""
        proceso = self.procesos[idx]
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar {proceso.nombre}")
        dialog.geometry("300x250")
        dialog.configure(bg="#1e1e2e")
        dialog.resizable(False, False)
        
        # Centrar ventana
        dialog.transient(self.master) # type: ignore
        dialog.grab_set()
        
        # Campos de edición
        fields = [
            ("Nombre:", proceso.nombre, "str"),
            ("Tiempo de llegada:", str(proceso.tiempo_llegada), "int"),
            ("Ráfaga:", str(proceso.rafaga), "int"),
            ("Prioridad:", str(proceso.prioridad) if proceso.prioridad else "", "int")
        ]
        
        entries = {}
        for i, (label, value, field_type) in enumerate(fields):
            tk.Label(dialog, text=label, bg="#1e1e2e", fg="#cdd6f4").grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            entry = tk.Entry(dialog, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4")
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[label] = (entry, field_type)
        
        # Algoritmo
        tk.Label(dialog, text="Algoritmo:", bg="#1e1e2e", fg="#cdd6f4").grid(
            row=len(fields), column=0, sticky="w", padx=10, pady=5
        )
        algo_var = tk.StringVar(value=proceso.algoritmo)
        algo_combo = ttk.Combobox(dialog, textvariable=algo_var, values=["FCFS", "Prioridades"], state="readonly")
        algo_combo.grid(row=len(fields), column=1, padx=10, pady=5, sticky="ew")
        
        dialog.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = tk.Frame(dialog, bg="#1e1e2e")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                # Validar y guardar cambios
                nombre = entries["Nombre:"][0].get().strip()
                tiempo_llegada = int(entries["Tiempo de llegada:"][0].get())
                rafaga = int(entries["Ráfaga:"][0].get())
                prioridad_str = entries["Prioridad:"][0].get().strip()
                prioridad = int(prioridad_str) if prioridad_str else None
                algoritmo = algo_var.get()
                
                if nombre and tiempo_llegada >= 0 and rafaga > 0:
                    # Aplicar cambios usando el callback
                    if self.on_edit:
                        self.on_edit(idx, "nombre", nombre)
                        self.on_edit(idx, "tiempo_llegada", tiempo_llegada)
                        self.on_edit(idx, "rafaga", rafaga)
                        self.on_edit(idx, "prioridad", prioridad)
                        self.on_edit(idx, "algoritmo", algoritmo)
                    
                    self.add_log_entry(f"📝 Proceso {nombre} editado")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Valores inválidos")
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        ttk.Button(btn_frame, text="Guardar", command=save_changes, style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, style="Error.TButton").pack(side="left", padx=5)

    def on_double_click(self, event: Any) -> None:
        """Maneja doble clic para edición rápida"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
            
        col_index = int(column.replace('#', '')) - 1
        columns = ("nombre", "tiempo_llegada", "rafaga", "prioridad", "algoritmo", 
                  "tiempo_inicio", "tiempo_final", "tiempo_retorno", "tiempo_espera")
        
        # Solo permitir edición de campos específicos
        if col_index in [0, 1, 2, 3, 4]:  # campos editables
            self.edit_cell_inline(item, column, col_index, columns[col_index])

    def edit_cell_inline(self, item: str, column: str, col_index: int, field_name: str) -> None:
        """Edita una celda inline"""
        try:
            x, y, width, height = self.tree.bbox(item, column)
            value = self.tree.set(item, column)
            
            if field_name == "algoritmo":
                # Combobox para algoritmo
                cb = ttk.Combobox(self.tree, values=["FCFS", "Prioridades"], state="readonly")
                cb.place(x=x, y=y, width=width, height=height)
                cb.set(value)
                cb.focus()
                
                def on_select(e):
                    new_value = cb.get()
                    if self.on_edit:
                        self.on_edit(int(item), field_name, new_value)
                    cb.destroy()
                
                cb.bind("<<ComboboxSelected>>", on_select)
                cb.bind('<FocusOut>', lambda e: cb.destroy())
            else:
                # Entry para otros campos
                entry = tk.Entry(self.tree, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4")
                entry.place(x=x, y=y, width=width, height=height)
                entry.insert(0, value)
                entry.focus()
                entry.select_range(0, tk.END)

                def on_enter(e: Any) -> None:
                    try:
                        new_value = entry.get().strip()
                        if field_name in ["tiempo_llegada", "rafaga"]:
                            new_value = int(new_value)
                        elif field_name == "prioridad":
                            new_value = int(new_value) if new_value else None

                        if self.on_edit:
                            self.on_edit(int(item), field_name, new_value)
                    except ValueError:
                        messagebox.showerror("Error", "Valor inválido")
                    finally:
                        entry.destroy()
                entry.bind('<Return>', on_enter)
                entry.bind('<FocusOut>', lambda e: entry.destroy())

        except tk.TclError:
            # Error si no se puede obtener bbox (elemento no visible)
            pass

    def refresh_table(self) -> None:
        """Refresca la tabla con los datos actuales"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Repoblar tabla
        for i, proceso in enumerate(self.procesos):
            # Solo mostrar procesos con ráfaga > 0
            if proceso.rafaga <= 0:
                continue

            # Mostrar ceros explícitamente para los tiempos
            values = (
                proceso.nombre,
                proceso.tiempo_llegada,
                proceso.rafaga,
                proceso.prioridad if proceso.prioridad is not None else "",
                proceso.algoritmo,
                proceso.tiempo_inicio,
                proceso.tiempo_final,
                proceso.tiempo_retorno,
                proceso.tiempo_espera
            )
            
            item_id = self.tree.insert("", "end", iid=str(i), values=values)
            
            # Colorear según estado del proceso
            if proceso.tiempo_final > 0 and proceso.tiempo_final <= self.tiempo_simulacion:
                # Proceso completado
                self.tree.item(item_id, tags=("completed",))
                self.tree.tag_configure("completed", foreground="#a6e3a1")  # Verde claro
            elif proceso.tiempo_inicio > 0 and proceso.tiempo_inicio <= self.tiempo_simulacion < proceso.tiempo_final:
                # Proceso en ejecución
                self.tree.item(item_id, tags=("running",))
                self.tree.tag_configure("running", foreground="#89b4fa")  # Azul claro
            elif proceso.tiempo_llegada <= self.tiempo_simulacion:
                # Proceso listo
                self.tree.item(item_id, tags=("ready",))
                self.tree.tag_configure("ready", foreground="#f9e2af")  # Amarillo

    def refresh(self, procesos: List[Proceso]) -> None:
        """Actualiza la vista con nuevos datos"""
        self.procesos = procesos
        self.refresh_table()
        self.update_metrics()
        
        # Actualizar Gantt
        if hasattr(self.gantt, 'procesos'):
            self.gantt.procesos = procesos
            self.gantt.draw_gantt(procesos, self.tiempo_simulacion)

    def actualizar(self, data: Any) -> None:
        """Método observer para recibir actualizaciones del modelo"""
        if isinstance(data, list):
            self.refresh(data)
        elif isinstance(data, dict):
            if 'tiempo' in data:
                self.actualizar_tiempo_simulacion(data['tiempo'])
            if 'procesos' in data:
                self.refresh(data['procesos'])
            if 'evento' in data:
                self.add_log_entry(data['evento'])

    def reset_simulation(self) -> None:
        """Resetea la simulación a estado inicial"""
        self.tiempo_simulacion = 0
        self.ejecutando = False
        self.pausado = False
        
        # Resetear controles
        self.update_control_buttons(False, True)
        self.btn_pause.configure(text="⏸ Pausar")
        
        # Limpiar log
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
        
        # Actualizar vista
        self.refresh_table()
        self.update_metrics()
        
        # Detener animación Gantt
        if hasattr(self.gantt, 'detener_animacion_dinamica'):
            self.gantt.detener_animacion_dinamica()

    def get_selected_process_index(self) -> Optional[int]:
        """Obtiene el índice del proceso seleccionado"""
        selection = self.tree.selection()
        if selection:
            return int(selection[0])
        return None

    def select_process(self, index: int) -> None:
        """Selecciona un proceso en la tabla"""
        if 0 <= index < len(self.procesos):
            self.tree.selection_set(str(index))
            self.tree.focus(str(index))

    def export_results(self) -> None:
        """Exporta los resultados a un archivo CSV"""
        from tkinter import filedialog
        import csv
        
        if not self.procesos:
            messagebox.showwarning("Advertencia", "No hay procesos para exportar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar resultados"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = ["Proceso", "Tiempo Llegada", "Ráfaga", "Prioridad", "Algoritmo",
                              "Tiempo Inicio", "Tiempo Final", "Tiempo Retorno", "Tiempo Espera"]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for proceso in self.procesos:
                        row = [
                            proceso.nombre,
                            proceso.tiempo_llegada,
                            proceso.rafaga,
                            proceso.prioridad if proceso.prioridad is not None else "",
                            proceso.algoritmo,
                            proceso.tiempo_inicio,
                            proceso.tiempo_final,
                            proceso.tiempo_retorno,
                            proceso.tiempo_espera
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Resultados exportados a {filename}")
                self.add_log_entry(f"📊 Resultados exportados a {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def show_statistics(self) -> None:
        """Muestra estadísticas detalladas"""
        if not self.procesos or not any(p.tiempo_final > 0 for p in self.procesos):
            messagebox.showwarning("Advertencia", "No hay datos de simulación para mostrar")
            return
        
        stats_window = tk.Toplevel(self)
        stats_window.title("Estadísticas Detalladas")
        stats_window.geometry("400x300")
        stats_window.configure(bg="#1e1e2e")
        stats_window.transient(self.master) # type: ignore
        
        # Calcular estadísticas
        procesos_completados = [p for p in self.procesos if p.tiempo_final > 0]
        
        if not procesos_completados:
            return
        
        tiempos_espera = [p.tiempo_espera for p in procesos_completados]
        tiempos_retorno = [p.tiempo_retorno for p in procesos_completados]
        
        promedio_espera = sum(tiempos_espera) / len(tiempos_espera)
        promedio_retorno = sum(tiempos_retorno) / len(tiempos_retorno)
        
        throughput = len(procesos_completados) / max(p.tiempo_final for p in procesos_completados)
        
        # Crear contenido
        content = f"""
        ESTADÍSTICAS DE SIMULACIÓN
        
        📊 Procesos Completados: {len(procesos_completados)}
        ⏱️ Total de Procesos: {len(self.procesos)}
        
        TIEMPOS PROMEDIO:
        • Tiempo de Espera: {promedio_espera:.2f}
        • Tiempo de Retorno: {promedio_retorno:.2f}
        
        RENDIMIENTO:
        • Throughput: {throughput:.2f} procesos/unidad
        
        DETALLES POR PROCESO:
        """
        
        for p in procesos_completados:
            content += f"\n{p.nombre}: Espera={p.tiempo_espera}, Retorno={p.tiempo_retorno}"
        
        text_widget = tk.Text(
            stats_window,
            bg="#313244",
            fg="#cdd6f4",
            font=("JetBrains Mono", 10),
            padx=20,
            pady=20,
            state="disabled"
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        
        text_widget.configure(state="normal")
        text_widget.insert(1.0, content)
        text_widget.configure(state="disabled")

    def toggle_dark_mode(self) -> None:
        """Alterna entre modo oscuro y claro"""
        # Esta funcionalidad se puede implementar cambiando los colores de todos los widgets
        # Por simplicidad, solo mostramos un mensaje
        messagebox.showinfo("Modo Oscuro", "El modo oscuro ya está activado por defecto")

    def show_help(self) -> None:
        """Muestra la ayuda del simulador"""
        help_window = tk.Toplevel(self)
        help_window.title("Ayuda - Simulador de Procesos")
        help_window.geometry("500x400")
        help_window.configure(bg="#1e1e2e")
        help_window.transient(self.master) # type: ignore
        
        help_text = """
        SIMULADOR DE PLANIFICACIÓN DE PROCESOS
        
        🔧 CONTROLES PRINCIPALES:
        • ▶ Ejecutar: Inicia la simulación
        • ⏸ Pausar: Pausa/reanuda la simulación
        • ⏹ Detener: Detiene y resetea la simulación
        • Velocidad: Controla la velocidad de simulación
        
        📋 GESTIÓN DE PROCESOS:
        • Agregar Proceso: Crea un nuevo proceso
        • Doble clic: Edita un proceso inline
        • Clic derecho: Menú contextual con opciones
        
        📊 ALGORITMOS SOPORTADOS:
        • FCFS: First Come First Served
        • Prioridades: Planificación por prioridades
        
        📈 DIAGRAMA DE GANTT:
        • Verde: Proceso completado
        • Azul: Proceso en ejecución
        • Amarillo: Proceso pendiente
        • Línea roja: Tiempo actual
        
        💡 CONSEJOS:
        • Los procesos se pueden agregar durante la ejecución
        • Los cambios se aplican dinámicamente
        • Use el log para seguir los eventos
        • Exporte los resultados para análisis
        """
        
        text_widget = tk.Text(
            help_window,
            bg="#313244",
            fg="#cdd6f4",
            font=("Segoe UI", 10),
            padx=20,
            pady=20,
            state="disabled",
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        
        text_widget.configure(state="normal")
        text_widget.insert(1.0, help_text)
        text_widget.configure(state="disabled")

    def cleanup(self) -> None:
        """Limpia recursos antes de cerrar"""
        # Detener animación Gantt
        if hasattr(self.gantt, 'detener_animacion_dinamica'):
            self.gantt.detener_animacion_dinamica()
        
        # Limpiar callbacks
        self.on_edit = None
        self.on_add = None
        self.on_run = None
        self.on_pause = None
        self.on_stop = None
        self.on_speed_change = None
        self.on_reset = None

    def on_add_fcfs_clicked(self) -> None:
        """Callback para el botón de agregar FCFS"""
        if self.on_add_fcfs:
            self.on_add_fcfs()
        self.add_log_entry("➕ Proceso FCFS agregado")

    def on_add_prioridad_clicked(self) -> None:
        """Callback para el botón de agregar Prioridad"""
        if self.on_add_prioridad:
            self.on_add_prioridad()
        self.add_log_entry("➕ Proceso de Prioridad agregado")