from view.vista import ProcesoTableView
from model.proceso import Proceso
from model.fcfs import FCFS
from model.prioridades import Prioridades
from model.planificador import Planificador
import tkinter as tk
from typing import List, Any

class Controller:
    def __init__(self) -> None:
        self.planificador: Planificador = FCFS()  # Podemos cambiar esto por cualquier otro algoritmo en el futuro
        self.root = tk.Tk()
        self.root.title("Planificador de Procesos")
        self.procesos: List[Proceso] = [
            # Proceso("P1", 0, 5,"FCFS"),
            # Proceso("P2", 2, 3,"FCFS"),
            # Proceso("P3", 4, 1,"FCFS")
            Proceso("P1", 0, 5,"Prioridades", 1),
            Proceso("P2", 2, 3,"Prioridades",4),
            Proceso("P3", 4, 1,"Prioridades",3),
            Proceso("P4", 4, 1,"Prioridades",2)

        ]
        self.view = ProcesoTableView(
            master=self.root,
            procesos=self.procesos,
            on_edit=self.on_edit,
            on_add=self.add_proceso,
            on_run=self.ejecutar_planificador
        )
        # Registrar la vista como observador
        self.planificador.add_observer(self.view)

    def add_proceso(self) -> None:
        nuevo_nombre: str = f"P{len(self.procesos)+1}"
        # nuevo = Proceso(nuevo_nombre, 0, 1, "FCFS")#Aqui se cambia para el test
        nuevo = Proceso(nuevo_nombre, 0, 1,"Prioridades",2)
        self.procesos.append(nuevo)
        self.view.refresh(self.procesos)
        # No recalcular tiempos aquí, solo al ejecutar el planificador

    def on_edit(self, idx: int, field: str, value: Any) -> None:
        proceso: Proceso = self.procesos[idx]
        if field == "nombre":
            proceso.nombre = value
        elif field == "tiempo_llegada":
            proceso.tiempo_llegada = int(value)
        elif field == "rafaga":
            proceso.rafaga = int(value)
        elif field == "prioridad":
            proceso.prioridad = int(value) if value != '' else None
        elif field == "algoritmo":
            proceso.algoritmo = value
        self.view.refresh(self.procesos)
        # No recalcular tiempos aquí, solo al ejecutar el planificador

    def ejecutar_planificador(self) -> None:
        # Separar procesos pendientes por algoritmo
        procesos_fcfs: List[Proceso] = [p for p in self.procesos if p.algoritmo == "FCFS" and p.tiempo_final == 0]
        procesos_prioridad: List[Proceso] = [p for p in self.procesos if p.algoritmo == "Prioridades" and p.tiempo_final == 0]

        # Ejecutar FCFS solo en pendientes
        if procesos_fcfs:
            planificador_fcfs = FCFS()
            for p in procesos_fcfs:
                planificador_fcfs.add_proceso(p)
            resultado_fcfs: List[Proceso] = planificador_fcfs.run()
            for i, p in enumerate(procesos_fcfs):
                p.tiempo_inicio = resultado_fcfs[i].tiempo_inicio
                p.tiempo_final = resultado_fcfs[i].tiempo_final
                p.tiempo_retorno = resultado_fcfs[i].tiempo_retorno
                p.tiempo_espera = resultado_fcfs[i].tiempo_espera

        # Ejecutar Prioridades solo en pendientes
        if procesos_prioridad:
            planificador_prio = Prioridades()
            for p in procesos_prioridad:
                planificador_prio.add_proceso(p)
            resultado_prio: List[Proceso] = planificador_prio.run()
            # Actualizar los procesos originales por nombre
            for p_result in resultado_prio:
                for p_orig in self.procesos:
                    if p_orig.nombre == p_result.nombre:
                        p_orig.tiempo_inicio = p_result.tiempo_inicio
                        p_orig.tiempo_final = p_result.tiempo_final
                        p_orig.tiempo_retorno = p_result.tiempo_retorno
                        p_orig.tiempo_espera = p_result.tiempo_espera
                        break

        # Actualizar la vista y animar el Gantt
        self.view.refresh(self.procesos)
        self.view.gantt.animar(self.procesos, velocidad=0.2)

    def run(self) -> None:
        self.root.mainloop()
