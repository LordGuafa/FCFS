import tkinter as tk
from typing import List, Dict, Optional
from model.proceso import Proceso
import threading

class GanttChart(tk.Frame):
    def __init__(self, master, procesos: List[Proceso]) -> None:
        super().__init__(master)
        self.scroll_x = tk.Scrollbar(self, orient="horizontal")
        self.scroll_y = tk.Scrollbar(self, orient="vertical")
        self.canvas = tk.Canvas(self, width=700, height=40 + 50 * len(procesos), bg="white",
                               xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.procesos = procesos
        self.animando = False
        self.tiempo_actual_animacion = 0
        self.velocidad_animacion = 1.0
        self.animation_thread = None
        self.detener_animacion = False
        
        self.draw_gantt(procesos)

        # Soporte para scroll con el mouse
        self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows)
        self.canvas.bind("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", self._on_mousewheel_linux_down)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel_windows)
        self.canvas.bind("<Shift-Button-4>", self._on_shift_mousewheel_linux_left)
        self.canvas.bind("<Shift-Button-5>", self._on_shift_mousewheel_linux_right)

    def draw_gantt(self, procesos: List[Proceso], tiempo_actual: int = 0) -> None:
        """Dibuja el diagrama de Gantt con progreso en tiempo real"""
        self.procesos = procesos  # <-- Asegura que la lista esté actualizada
        self.canvas.delete("all")
        if not procesos:
            return

        # Mostrar todos los procesos con ráfaga > 0
        procesos_con_tiempo = [p for p in procesos if p.rafaga > 0]
        if not procesos_con_tiempo:
            return

        min_ti = min((p.tiempo_inicio for p in procesos_con_tiempo), default=0)
        max_tf = max((p.tiempo_final for p in procesos_con_tiempo), default=0)
        max_tf = max(max_tf, tiempo_actual + 5)
        total_time = max_tf - min_ti

        x0 = 80
        y0 = 40
        height = 30
        scale = 40  # Escala ajustable

        # Ajustar el tamaño del canvas dinámicamente según la cantidad de procesos
        canvas_width = x0 + int(total_time * scale) + 100
        canvas_height = y0 + len(procesos) * 50 + 100
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

        # Dibujar línea de tiempo actual
        if tiempo_actual >= 0:
            x_actual = x0 + scale * (tiempo_actual - min_ti)
            self.canvas.create_line(
                x_actual, y0 - 30, x_actual, y0 + len(procesos) * 50,
                fill="red", width=3, tags="tiempo_actual"
            )
            self.canvas.create_text(
                x_actual, y0 - 35, text=f"T={tiempo_actual}",
                font=("Arial", 10, "bold"), fill="red"
            )

        # Dibujar procesos
        for idx, p in enumerate(procesos):
            y = y0 + idx * 50

            if p.rafaga > 0:
                x_inicio = x0 + scale * (p.tiempo_inicio - min_ti)
                x_fin = x0 + scale * (p.tiempo_final - min_ti)

                # Fondo de la barra (gris claro)
                self.canvas.create_rectangle(
                    x_inicio, y, x_fin, y + height,
                    fill="#e8e8e8", outline="#cccccc", width=1
                )

                # Barra de progreso (según el estado)
                if p.tiempo_final > 0 and tiempo_actual >= p.tiempo_final:
                    # Proceso completado
                    color_fill = "#4CAF50"  # Verde
                    color_outline = "#2E7D32"
                    self.canvas.create_rectangle(
                        x_inicio, y, x_fin, y + height,
                        fill=color_fill, outline=color_outline, width=2
                    )
                elif p.tiempo_inicio > 0 and tiempo_actual >= p.tiempo_inicio and tiempo_actual < p.tiempo_final:
                    # Proceso en ejecución
                    progreso = min(tiempo_actual, p.tiempo_final)
                    x_progreso = x0 + scale * (progreso - min_ti)
                    color_fill = "#2196F3"  # Azul
                    color_outline = "#1565C0"
                    self.canvas.create_rectangle(
                        x_inicio, y, x_progreso, y + height,
                        fill=color_fill, outline=color_outline, width=2
                    )
                elif p.tiempo_llegada <= tiempo_actual:
                    # Proceso listo pero no iniciado
                    color_fill = "#FFC107"  # Amarillo
                    color_outline = "#F57C00"
                    self.canvas.create_rectangle(
                        x_inicio, y, x_fin, y + height,
                        fill=color_fill, outline=color_outline, width=2
                    )

                # Texto del proceso
                text_x = x_inicio + (x_fin - x_inicio) / 2
                self.canvas.create_text(
                    text_x, y + height/2, text=p.nombre,
                    font=("Arial", 10, "bold"), fill="white"
                )

                # Etiquetas de tiempo
                self.canvas.create_text(
                    x_inicio, y + height + 10, text=str(p.tiempo_inicio),
                    font=("Arial", 8), anchor="n"
                )
                self.canvas.create_text(
                    x_fin, y + height + 10, text=str(p.tiempo_final),
                    font=("Arial", 8), anchor="n"
                )

            # Nombre del proceso (siempre visible)
            self.canvas.create_text(
                x0 - 50, y + height/2, text=p.nombre,
                font=("Arial", 11, "bold"), anchor="w"
            )

            # Información adicional
            info_text = f"Llegada: {p.tiempo_llegada}"
            if p.prioridad is not None:
                info_text += f", Prioridad: {p.prioridad}"
            if p.tiempo_espera > 0:
                info_text += f", Espera: {p.tiempo_espera}"

            self.canvas.create_text(
                x0 - 50, y + height + 20, text=info_text,
                font=("Arial", 8), anchor="w", fill="gray"
            )

        # Eje de tiempo
        for t in range(int(min_ti), int(max_tf) + 1):
            xt = x0 + (t - min_ti) * scale
            self.canvas.create_line(
                xt, y0 - 20, xt, y0 + len(procesos) * 50,
                fill="#dddddd", dash=(1, 2)
            )
            self.canvas.create_text(
                xt, y0 - 25, text=str(t),
                font=("Arial", 9)
            )

    def animar_dinamico(self, procesos: List[Proceso], velocidad: float = 1.0) -> None:
        """Inicia la animación dinámica del diagrama de Gantt"""
        self.procesos = procesos
        self.velocidad_animacion = velocidad
        self.tiempo_actual_animacion = 0
        self.detener_animacion = False
        
        if not self.animando:
            self.animando = True
            self.animation_thread = threading.Thread(target=self._loop_animacion)
            self.animation_thread.daemon = True
            self.animation_thread.start()

    def _loop_animacion(self) -> None:
        """Loop principal de la animación"""
        import time
        while self.animando and not self.detener_animacion:
            # Recalcular el tiempo final máximo en cada ciclo para incluir procesos nuevos
            procesos_con_final = [p for p in self.procesos if p.tiempo_final > 0]
            if not procesos_con_final:
                break
            tiempo_final_max = max(p.tiempo_final for p in procesos_con_final)

            # Actualizar en el hilo principal de tkinter
            self.after(0, self._actualizar_frame)
            time.sleep(self.velocidad_animacion)
            self.tiempo_actual_animacion += 1

            # Detener cuando se haya mostrado el último tick de todos los procesos
            if self.tiempo_actual_animacion > tiempo_final_max:
                break

        # Asegura que el último frame se dibuje exactamente en el tiempo final máximo
        procesos_con_final = [p for p in self.procesos if p.tiempo_final > 0]
        if procesos_con_final:
            tiempo_final_max = max(p.tiempo_final for p in procesos_con_final)
            self.tiempo_actual_animacion = tiempo_final_max
            self.after(0, self._actualizar_frame)

        self.animando = False

    def _actualizar_frame(self) -> None:
        """Actualiza un frame de la animación"""
        self.draw_gantt(self.procesos, self.tiempo_actual_animacion)

    def detener_animacion_dinamica(self) -> None:
        """Detiene la animación dinámica"""
        self.detener_animacion = True
        self.animando = False
        self.tiempo_actual_animacion = 0

    def actualizar_tiempo(self, tiempo: int) -> None:
        """Actualiza el tiempo actual de la simulación"""
        self.tiempo_actual_animacion = tiempo
        self.draw_gantt(self.procesos, tiempo)

    # Mantener compatibilidad con la función original
    def animar(self, procesos: List[Proceso], callback=None, velocidad=0.1) -> None:
        """Función de animación original para compatibilidad"""
        self.animar_dinamico(procesos, velocidad)

    # Scroll vertical (Windows y Mac)
    def _on_mousewheel_windows(self, event):
        if event.state & 0x0001:  # Shift presionado
            self.canvas.xview_scroll(-1 * int(event.delta / 120), "units")
        else:
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Scroll horizontal con Shift (Windows y Mac)
    def _on_shift_mousewheel_windows(self, event):
        self.canvas.xview_scroll(-1 * int(event.delta / 120), "units")

    # Scroll vertical (Linux)
    def _on_mousewheel_linux_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        self.canvas.yview_scroll(1, "units")

    # Scroll horizontal con Shift (Linux)
    def _on_shift_mousewheel_linux_left(self, event):
        self.canvas.xview_scroll(-1, "units")

    def _on_shift_mousewheel_linux_right(self, event):
        self.canvas.xview_scroll(1, "units")