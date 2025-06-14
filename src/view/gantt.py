import tkinter as tk
from typing import List
from model.proceso import Proceso

class GanttChart(tk.Toplevel):
    def __init__(self, master, procesos: List[Proceso]) -> None: #type:ignore
        super().__init__(master) #type:ignore
        self.title("Diagrama de Gantt")
        self.geometry("600x150")
        self.canvas = tk.Canvas(self, width=580, height=100, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.draw_gantt(procesos)

    def draw_gantt(self, procesos: List[Proceso]):
        if not procesos:
            return
        min_ti = min(p.TI for p in procesos)
        max_tf = max(p.TF for p in procesos)
        total_time = max_tf - min_ti
        x0 = 20
        y0 = 40
        height = 40
        scale = 500 / (total_time if total_time > 0 else 1)
        for p in procesos:
            start = x0 + (p.TI - min_ti) * scale
            end = x0 + (p.TF - min_ti) * scale
            self.canvas.create_rectangle(start, y0, end, y0 + height, fill="#87CEEB", outline="black")
            self.canvas.create_text((start + end) / 2, y0 + height / 2, text=p.nombre)
            self.canvas.create_text(start, y0 + height + 10, text=str(int(p.TI)), anchor="n")
        self.canvas.create_text(x0 + (procesos[-1].TF - min_ti) * scale, y0 + height + 10, text=str(int(procesos[-1].TF)), anchor="n")
