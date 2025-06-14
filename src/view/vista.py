import tkinter as tk
from tkinter import ttk
from model.proceso import Proceso
from typing import Callable, List, Optional, Any

class ProcesoTableView(tk.Frame):
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        procesos: Optional[List[Proceso]] = None,
        on_edit: Optional[Callable[[int, str, Any], None]] = None,
        on_add: Optional[Callable[[], None]] = None,
        on_run_fcfs: Optional[Callable[[], None]] = None
    ) -> None:
        super().__init__(master)
        self.master: Optional[tk.Misc] = master # type: ignore
        self.procesos: List[Proceso] = procesos if procesos is not None else []
        self.on_edit: Optional[Callable[[int, str, Any], None]] = on_edit
        self.on_add = on_add
        self.on_run_fcfs = on_run_fcfs
        self.pack()
        self.create_widgets()

    def create_widgets(self) -> None:
        columns = ("nombre", "TA", "R", "TI", "TF", "TR", "TE")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        for idx, p in enumerate(self.procesos):
            self.tree.insert("", "end", iid=idx, values=(p.nombre, p.TA, p.R, p.TI, p.TF, p.TR, p.TE))
        self.tree.pack(side="top", fill="x")
        self.tree.bind('<Double-1>', self.on_double_click)

        # Botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(side="top", fill="x", pady=10)
        btn_add = tk.Button(btn_frame, text="Agregar Proceso", command=self.on_add if self.on_add else lambda: None)
        btn_add.pack(side="left", padx=5)
        btn_run = tk.Button(btn_frame, text="Ejecutar FCFS", command=self.on_run_fcfs if self.on_run_fcfs else lambda: None)
        btn_run.pack(side="left", padx=5)

    def refresh(self, procesos: List[Proceso]) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, p in enumerate(procesos):
            self.tree.insert("", "end", iid=idx, values=(p.nombre, p.TA, p.R, p.TI, p.TF, p.TR, p.TE))

    def on_double_click(self, event: Any) -> None:
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace('#', '')) - 1
        editable_cols = [0, 1, 2]  # Solo nombre, TA, R
        columns = ("nombre", "TA", "R", "TI", "TF", "TR", "TE")
        if col_index in editable_cols:
            x, y, width, height = self.tree.bbox(item, column)
            value = self.tree.set(item, column)
            entry = tk.Entry(self.tree)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, value)
            entry.focus()
            def save_edit(e: Any) -> None:
                new_value = entry.get()
                self.tree.set(item, column, new_value)
                entry.destroy()
                if self.on_edit:
                    self.on_edit(int(item), columns[col_index], new_value)
            entry.bind('<Return>', save_edit)
            entry.bind('<FocusOut>', lambda e: entry.destroy())

