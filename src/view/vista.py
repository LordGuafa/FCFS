import tkinter as tk
from tkinter import ttk
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
        on_run: Optional[Callable[[], None]] = None
    ) -> None:
        super().__init__(master, bg="#232946")
        self.master: Optional[tk.Misc] = master # type: ignore
        self.procesos: List[Proceso] = procesos if procesos is not None else []
        self.on_edit: Optional[Callable[[int, str, Any], None]] = on_edit
        self.on_add: Callable[[], None] | None = on_add
        self.on_run: Callable[[], None] | None = on_run
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self) -> None:
        # Título
        lbl_title = tk.Label(self, text="Planificador de Procesos", font=("Arial", 14, "bold"), fg="#eebbc3", bg="#232946")
        lbl_title.pack(side="top", anchor="w", padx=10, pady=(10, 0))

        # Tabla
        columns = ("nombre", "tiempo_llegada", "rafaga", "prioridad", "algoritmo", "tiempo_inicio", "tiempo_final", "tiempo_retorno", "tiempo_espera")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#232946", fieldbackground="#232946", foreground="#eebbc3", rowheight=28, font=("Arial", 11))#type: ignore
        style.configure("Treeview.Heading", background="#121629", foreground="#eebbc3", font=("Arial", 11, "bold"))#type: ignore
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        for idx, p in enumerate(self.procesos):
            algoritmo = getattr(p, "algoritmo", "FCFS")
            self.tree.insert("", "end", iid=idx, values=(p.nombre, p.tiempo_llegada, p.rafaga, p.prioridad if p.prioridad is not None else "", algoritmo, p.tiempo_inicio, p.tiempo_final, p.tiempo_retorno, p.tiempo_espera))
        self.tree.pack(side="top", fill="x", padx=10, pady=5)
        self.tree.bind('<Double-1>', self.on_double_click)

        # Combobox para seleccionar algoritmo por proceso
        self.comboboxes = {}
        for idx, p in enumerate(self.procesos):
            algoritmo = getattr(p, "algoritmo", "FCFS")
            cb = ttk.Combobox(self.tree, values=["FCFS", "Prioridades"], state="readonly")
            cb.set(algoritmo)
            cb.bind("<<ComboboxSelected>>", lambda e, i=idx: self.on_algoritmo_selected(i, e))
            self.comboboxes[idx] = cb

        # Botones
        btn_frame = tk.Frame(self, bg="#232946")
        btn_frame.pack(side="top", fill="x", pady=10)
        btn_add = tk.Button(btn_frame, text="Agregar Proceso", command=self.on_add if self.on_add else lambda: None, bg="#eebbc3", fg="#232946", font=("Arial", 11, "bold"), activebackground="#393e6a")
        btn_add.pack(side="left", padx=10)
        btn_run = tk.Button(btn_frame, text="Ejecutar Planificador", command=self.on_run if self.on_run else lambda: None, bg="#a1ffce", fg="#232946", font=("Arial", 11, "bold"), activebackground="#393e6a")
        btn_run.pack(side="left", padx=10)

        # Diagrama de Gantt
        lbl_gantt = tk.Label(self, text="Diagrama de Gantt", font=("Arial", 14, "bold"), fg="#eebbc3", bg="#232946")
        lbl_gantt.pack(side="top", anchor="w", padx=10, pady=(10, 0))
        self.gantt = GanttChart(self, self.procesos)
        self.gantt.pack(side="top", fill="x", padx=10, pady=5)

        # Log de procesos pendientes
        log_frame = tk.Frame(self, bg="#232946")
        log_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        lbl_log = tk.Label(log_frame, text="Procesos pendientes:", font=("Arial", 12, "bold"), fg="#eebbc3", bg="#232946")
        lbl_log.pack(anchor="w")
        self.log_text = tk.Text(log_frame, height=6, bg="#121629", fg="#eebbc3", font=("Consolas", 11), state="disabled", borderwidth=2, relief="groove")
        self.log_text.pack(fill="both", expand=True)
        self.update_log(self.procesos)

    def update_from_model(self, procesos: List[Proceso]) -> None:
        """Método implementado como parte del patrón observador"""
        self.procesos = procesos
        self.refresh(procesos)

    def refresh(self, procesos: List[Proceso]) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, p in enumerate(procesos):
            self.tree.insert("", "end", iid=idx, values=(p.nombre, p.tiempo_llegada, p.rafaga, p.prioridad if p.prioridad is not None else "", p.algoritmo, p.tiempo_inicio, p.tiempo_final, p.tiempo_retorno, p.tiempo_espera))
        self.gantt.draw_gantt(procesos)
        self.update_log(procesos)

    def update_log(self, procesos: List[Proceso]) -> None:
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        for p in procesos:
            if p.tiempo_final == 0:
                self.log_text.insert(tk.END, f"{p.nombre} | Llegada: {p.tiempo_llegada} | Rafaga: {p.rafaga}\n")
        self.log_text.config(state="disabled")

    def on_double_click(self, event: Any) -> None:
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace('#', '')) - 1
        columns = ("nombre", "tiempo_llegada", "rafaga", "prioridad", "algoritmo", "tiempo_inicio", "tiempo_final", "tiempo_retorno", "tiempo_espera")
        # Editables: nombre, tiempo_llegada, rafaga, prioridad, algoritmo
        if col_index in [0, 1, 2, 3, 4]:
            x, y, width, height = self.tree.bbox(item, column)
            value = self.tree.set(item, column)
            if col_index == 4:  # Algoritmo
                cb = ttk.Combobox(self.tree, values=["FCFS", "Prioridades"], state="readonly")
                cb.place(x=x, y=y, width=width, height=height)
                cb.set(value)
                cb.focus()
                def on_select(e):
                    new_value = cb.get()
                    if self.on_edit:
                        self.on_edit(int(item), columns[col_index], new_value)
                    cb.destroy()
                cb.bind("<<ComboboxSelected>>", on_select)
                cb.bind('<FocusOut>', lambda e: cb.destroy())
            else:  # Para prioridad y otros campos editables
                entry = tk.Entry(self.tree)
                entry.place(x=x, y=y, width=width, height=height)
                entry.insert(0, value)
                entry.focus()
                def on_enter(e: Any) -> None:
                    if self.on_edit:
                        new_value = entry.get()
                        self.on_edit(int(item), columns[col_index], new_value)
                    entry.destroy()
                entry.bind('<Return>', on_enter)
                entry.bind('<FocusOut>', lambda e: entry.destroy())

    def on_algoritmo_selected(self, idx, event):
        value = self.comboboxes[idx].get()
        self.procesos[idx].algoritmo = value
        if self.on_edit:
            self.on_edit(idx, "algoritmo", value)

