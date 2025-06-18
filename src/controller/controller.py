from view.vista import ProcesoTableView
from model.proceso import Proceso
from model.fcfs import FCFS
import tkinter as tk
from typing import List, Any

class Controller:
    def __init__(self) -> None:
        self.fcfs = FCFS()
        self.root = tk.Tk()
        self.root.title("Tabla de Procesos")
        self.procesos: List[Proceso] = [
            Proceso("P1", 0, 5),
            Proceso("P2", 2, 3),
            Proceso("P3", 4, 1)
        ]
        self.view = ProcesoTableView(
            master=self.root,
            procesos=self.procesos,
            on_edit=self.on_edit,
            on_add=self.add_proceso,
            on_run_fcfs=self.ejecutar_fcfs
        )

    def add_proceso(self) -> None:
        nuevo_nombre: str = f"P{len(self.procesos)+1}"
        nuevo = Proceso(nuevo_nombre, 0, 1)
        self.procesos.append(nuevo)
        # Recalcula los tiempos para todos los procesos
        self.fcfs.recalcular_tiempos(self.procesos)
        self.update_procesos(self.procesos)
        # Si la animación está en curso, redibuja el Gantt para mostrar el nuevo proceso
        if getattr(self.view.gantt, "animando", False):
            self.view.gantt.draw_gantt(self.procesos)

    def on_edit(self, idx: int, field: str, value: Any) -> None:
        proceso: Proceso = self.procesos[idx]
        if field == "nombre":
            proceso.nombre = value
        elif field == "TA":
            proceso.TA = int(value)
        elif field == "R":
            proceso.R = int(value)
        elif field == "TI":
            proceso.TI = int(value)
        elif field == "TF":
            proceso.TF = int(value)
        elif field == "TR":
            proceso.TR = int(value)
        elif field == "TE":
            proceso.TE = int(value)
        self.update_procesos(self.procesos)

    def ejecutar_fcfs(self) -> None:
        self.fcfs.lista_procesos.clear()
        for p in self.procesos:
            self.fcfs.add_proceso(p)
        resultado: List[Proceso] = self.fcfs.run()
        self.update_procesos(resultado)
        # Animar el Gantt
        self.view.gantt.animar(self.procesos, callback=None, velocidad=0.2)#type: ignore

    def update_procesos(self, resultado: List[Proceso]) -> None:
        for i, p in enumerate(resultado):
                self.procesos[i].TI = p.TI
                self.procesos[i].TF = p.TF
                self.procesos[i].TR = p.TR
                self.procesos[i].TE = p.TE
        self.view.refresh(self.procesos)

    def run(self) -> None:
        self.root.mainloop()
