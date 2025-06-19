import tkinter as tk
from typing import List, Dict, Optional
from model.proceso import Proceso

class GanttChart(tk.Frame):
    def __init__(self, master, procesos: List[Proceso]) -> None: #type: ignore
        super().__init__(master)#type: ignore
        self.scroll_x = tk.Scrollbar(self, orient="horizontal")
        self.scroll_y = tk.Scrollbar(self, orient="vertical")
        self.canvas = tk.Canvas(self, width=700, height=40 + 50 * len(procesos), bg="white",
                               xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)#type: ignore
        self.scroll_y.config(command=self.canvas.yview)#type: ignore
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.procesos = procesos
        self.animando = False
        self.draw_gantt(procesos)

    def draw_gantt(self, procesos: List[Proceso], progreso: Optional[Dict[str, int]] = None) -> None:
        self.canvas.delete("all")
        if not procesos:
            return
        min_ti = min(p.tiempo_inicio for p in procesos)
        max_tf = max(p.tiempo_final for p in procesos)
        total_time = max_tf - min_ti
        x0 = 60
        y0 = 40
        height = 30
        scale = 60  # 1 unidad de tiempo = 60px (ajustable)
        canvas_width = x0 + int(total_time * scale) + 100
        canvas_height = y0 + len(procesos) * 50 + 50
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        for idx, p in enumerate(procesos):
            y = y0 + idx * 50
            barra_fin = progreso[p.nombre] if progreso and p.nombre in progreso else None

            # Solo dibuja la barra si el proceso ya ha comenzado a ejecutarse
            if barra_fin is not None and barra_fin > p.tiempo_inicio:
                # Fondo de la barra (gris)
                self.canvas.create_rectangle(
                    x0 + scale * (p.tiempo_inicio - min_ti), y,
                    x0 + scale * (p.tiempo_final - min_ti), y + height,
                    fill="#e0e0e0", outline="#b0b0b0"
                )
                # Barra de progreso (azul)
                self.canvas.create_rectangle(
                    x0 + scale * (p.tiempo_inicio - min_ti), y,
                    x0 + scale * (min(barra_fin, p.tiempo_final) - min_ti), y + height,
                    fill="#87CEEB", outline="#393e6a", width=2
                )
                # Tiempos solo si el proceso ya inició
                self.canvas.create_text(x0 - 10, y + height + 5, text=str(int(p.tiempo_inicio)), anchor="n", font=("Arial", 9))
                self.canvas.create_text(x0 + scale * (p.tiempo_final - min_ti), y + height + 5, text=str(int(p.tiempo_final)), anchor="n", font=("Arial", 9))
            # Nombre (siempre)
            self.canvas.create_text(x0 - 40, y + height / 2, text=p.nombre, font=("Arial", 11, "bold"), anchor="w")
        # Eje de tiempo
        for t in range(int(min_ti), int(max_tf)+1, max(1, int(total_time/10))):
            xt = x0 + (t - min_ti) * scale
            self.canvas.create_line(xt, y0 - 20, xt, y0 + len(procesos) * 50, fill="#b0b0b0", dash=(2,2))
            self.canvas.create_text(xt, y0 - 25, text=str(t), font=("Arial", 9))

    def animar(self, procesos: List[Proceso], callback=None, velocidad=0.1) -> None:  # type: ignore
        self.animando = True
        self._procesos_animados = set()
        progreso: Dict[str, int] = {}
        def avanzar():
            # Obtiene la lista actualizada de procesos ordenados por tiempo_inicio
            procesos_ordenados = sorted(procesos, key=lambda p: p.tiempo_inicio)
            for p in procesos_ordenados:
                if p.nombre in self._procesos_animados:
                    continue
                # Espera hasta que sea el turno de este proceso
                tiempo = p.tiempo_inicio
                def paso():
                    nonlocal tiempo
                    if tiempo < p.tiempo_final:
                        tiempo += 1
                        progreso[p.nombre] = tiempo
                        self.draw_gantt(procesos, progreso)
                        self.after(int(velocidad * 1000), paso)
                    else:
                        progreso[p.nombre] = p.tiempo_final
                        self.draw_gantt(procesos, progreso)
                        self._procesos_animados.add(p.nombre)
                        self.after(300, avanzar)
                paso()
                return  # Sale para esperar a que termine este proceso antes de continuar
            # Si ya no hay más procesos por animar
            self.animando = False
            if callback:
                callback()
        avanzar()
