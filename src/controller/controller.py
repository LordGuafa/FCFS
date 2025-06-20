from view.vista import ProcesoTableView
from model.proceso import Proceso
from model.fcfs import FCFS
from model.prioridades import Prioridades
from model.planificador import Planificador
import tkinter as tk
from typing import List, Any
import threading
import time
from utils.logger import setup_logger  # <--- Importar logger

class Controller:
    def __init__(self) -> None:
        self.planificador: Planificador = FCFS()
        self.root = tk.Tk()
        self.root.title("Planificador de Procesos - Simulación Dinámica")
        self.default_procesos = [
            Proceso("P1", 0, 5, "FCFS"),
            Proceso("P2", 2, 3, "FCFS"),
            Proceso("P3", 4, 1, "FCFS"),
        ]
        self.procesos: List[Proceso] = [Proceso(p.nombre, p.tiempo_llegada, p.rafaga, p.algoritmo, p.prioridad) for p in self.default_procesos]
        
        # Variables para controlar la ejecución
        self.ejecutando = False
        self.pausar_ejecucion = False
        self.tiempo_actual_simulacion = 0
        self.velocidad_simulacion = 1.0  # segundos por unidad de tiempo
        self.thread_ejecucion = None
        self.lock = threading.Lock()  # Para thread safety
        
        self.view = ProcesoTableView(
            master=self.root,
            procesos=self.procesos,
            on_edit=self.on_edit,
            on_add=self.add_proceso,
            on_run=self.ejecutar_planificador,
            on_pause=self.pausar_reanudar,
            on_stop=self.detener_ejecucion,
            on_speed_change=self.cambiar_velocidad,
            on_reset=self.reiniciar_simulacion  # <--- Nuevo callback
        )
        
        self.planificador.add_observer(self.view)
        self.logger = setup_logger()  # <--- Instanciar logger

    def add_proceso(self) -> None:
        """Agregar proceso durante la ejecución"""
        with self.lock:
            nuevo_nombre: str = f"P{len(self.procesos)+1}"
            # Si está ejecutando, el nuevo proceso llega en el tiempo actual de simulación
            tiempo_llegada = self.tiempo_actual_simulacion if self.ejecutando else 0
            nuevo = Proceso(nuevo_nombre, tiempo_llegada, 1, "FCFS")
            self.procesos.append(nuevo)
            
            # Si está ejecutando, recalcular inmediatamente
            if self.ejecutando:
                self.recalcular_durante_ejecucion()
            
            self.view.refresh(self.procesos)

    def on_edit(self, idx: int, field: str, value: Any) -> None:
        """Editar proceso existente"""
        with self.lock:
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
            
            # Si está ejecutando, recalcular
            if self.ejecutando:
                self.recalcular_durante_ejecucion()
            
            self.view.refresh(self.procesos)

    def recalcular_durante_ejecucion(self) -> None:
        """Recalcula los procesos que aún no han terminado"""
        # Resetear solo los procesos que no han comenzado o están en ejecución
        for proceso in self.procesos:
            if proceso.tiempo_inicio > self.tiempo_actual_simulacion:
                # Proceso que aún no ha comenzado
                proceso.tiempo_inicio = 0
                proceso.tiempo_final = 0
                proceso.tiempo_retorno = 0
                proceso.tiempo_espera = 0
        
        # Recalcular algoritmos
        self.calcular_algoritmos_dinamico()

    def calcular_algoritmos_dinamico(self) -> None:
        """Calcula los algoritmos considerando el tiempo actual de simulación"""
        # Procesos FCFS pendientes (que no han terminado)
        procesos_fcfs_pendientes = [
            p for p in self.procesos 
            if p.algoritmo == "FCFS" and 
            (p.tiempo_final == 0 or p.tiempo_final > self.tiempo_actual_simulacion)
        ]
        
        if procesos_fcfs_pendientes:
            planificador_fcfs = FCFS()
            planificador_fcfs.tiempo_inicial = self.tiempo_actual_simulacion

            # Agregar referencias a los mismos objetos, no copias
            for p in procesos_fcfs_pendientes:
                planificador_fcfs.add_proceso(p)

            resultado_fcfs = planificador_fcfs.run()
            # Actualizar los procesos originales con los resultados
            self.actualizar_procesos_desde_resultado(procesos_fcfs_pendientes, resultado_fcfs)
            self.logger.info("Procesos FCFS calculados:")
            for p in resultado_fcfs:
                self.logger.info(
                    f"{p.nombre} | Llegada: {p.tiempo_llegada} | Rafaga: {p.rafaga} | "
                    f"Inicio: {p.tiempo_inicio} | Final: {p.tiempo_final} | "
                    f"Retorno: {p.tiempo_retorno} | Espera: {p.tiempo_espera}"
                )

        # Procesos de Prioridades
        procesos_prioridades = [
            p for p in self.procesos 
            if p.algoritmo == "Prioridades" and p.prioridad is not None
        ]
        
        if procesos_prioridades:
            planificador_prio = Prioridades()
            planificador_prio.tiempo_inicial = self.tiempo_actual_simulacion

            for p in procesos_prioridades:
                planificador_prio.add_proceso(p)

            resultado_prio = planificador_prio.run()
            self.actualizar_procesos_desde_resultado(procesos_prioridades, resultado_prio)
            self.logger.info("Procesos Prioridades calculados:")
            for p in resultado_prio:
                self.logger.info(
                    f"{p.nombre} | Llegada: {p.tiempo_llegada} | Rafaga: {p.rafaga} | Prioridad: {p.prioridad} | "
                    f"Inicio: {p.tiempo_inicio} | Final: {p.tiempo_final} | "
                    f"Retorno: {p.tiempo_retorno} | Espera: {p.tiempo_espera}"
                )
            # Reordenar self.procesos para que los procesos de prioridades estén en el orden calculado
            # y los de FCFS mantengan su orden original
            nuevos_procesos = []
            # Primero, los procesos FCFS en su orden original
            for p in self.procesos:
                if p.algoritmo == "FCFS":
                    nuevos_procesos.append(p)
            # Luego, los procesos de prioridades en el orden calculado por el algoritmo
            for p in resultado_prio:
                nuevos_procesos.append(p)
            self.procesos = nuevos_procesos
            self.view.refresh(self.procesos)

    def actualizar_procesos_desde_resultado(self, procesos_originales: List[Proceso], resultado: List[Proceso]) -> None:
        """Actualiza los procesos originales con los resultados calculados"""
        # Asegura que los objetos originales se actualicen en sus atributos
        for p_result in resultado:
            for p_orig in procesos_originales:
                if p_orig.nombre == p_result.nombre:
                    p_orig.tiempo_inicio = p_result.tiempo_inicio
                    p_orig.tiempo_final = p_result.tiempo_final
                    p_orig.tiempo_retorno = p_result.tiempo_retorno
                    p_orig.tiempo_espera = p_result.tiempo_espera
                    # No reemplazar el objeto, solo actualizar atributos
                    break

    def ejecutar_planificador(self) -> None:
        """Inicia la ejecución en tiempo real"""
        if not self.ejecutando:
            self.ejecutando = True
            self.pausar_ejecucion = False
            self.tiempo_actual_simulacion = 0
            
            # Calcular inicialmente
            self.calcular_algoritmos_dinamico()
            
            # Iniciar thread de ejecución
            self.thread_ejecucion = threading.Thread(target=self.ejecutar_simulacion)
            self.thread_ejecucion.daemon = True
            self.thread_ejecucion.start()
            
            # Iniciar animación Gantt
            self.view.gantt.animar_dinamico(self.procesos, self.velocidad_simulacion)

    def ejecutar_simulacion(self) -> None:
        """Ejecuta la simulación en tiempo real"""
        while self.ejecutando:
            if not self.pausar_ejecucion:
                with self.lock:
                    self.tiempo_actual_simulacion += 1
                    
                    # Verificar si todos los procesos han terminado
                    procesos_terminados = all(
                        p.tiempo_final <= self.tiempo_actual_simulacion and p.tiempo_final > 0 
                        for p in self.procesos if p.rafaga > 0  # Solo considerar procesos con ráfaga > 0
                    )
                    
                    if procesos_terminados:
                        self.ejecutando = False
                        self.root.after(0, lambda: self.view.update_control_buttons(False, True))
                        break
                    
                    # Actualizar vista en el hilo principal
                    self.root.after(0, lambda: self.view.actualizar_tiempo_simulacion(self.tiempo_actual_simulacion))
                    self.root.after(0, lambda: self.view.gantt.actualizar_tiempo(self.tiempo_actual_simulacion))
                
                time.sleep(1.0 / self.velocidad_simulacion)  # Invertir la relación velocidad/tiempo
            else:
                time.sleep(0.1)

    def pausar_reanudar(self) -> None:
        """Pausa o reanuda la ejecución"""
        if self.ejecutando:
            self.pausar_ejecucion = not self.pausar_ejecucion

    def detener_ejecucion(self) -> None:
        """Detiene completamente la ejecución"""
        self.ejecutando = False
        self.pausar_ejecucion = False
        self.tiempo_actual_simulacion = 0
        
        # Resetear todos los procesos
        for proceso in self.procesos:
            proceso.tiempo_inicio = 0
            proceso.tiempo_final = 0
            proceso.tiempo_retorno = 0
            proceso.tiempo_espera = 0
        
        self.view.refresh(self.procesos)

    def cambiar_velocidad(self, nueva_velocidad: float) -> None:
        """Cambia la velocidad de simulación"""
        self.velocidad_simulacion = nueva_velocidad

    def reiniciar_simulacion(self) -> None:
        """Reinicia la simulación y restaura los valores predeterminados"""
        self.ejecutando = False
        self.pausar_ejecucion = False
        self.tiempo_actual_simulacion = 0
        # Restaurar procesos por defecto
        self.procesos = [Proceso(p.nombre, p.tiempo_llegada, p.rafaga, p.algoritmo, p.prioridad) for p in self.default_procesos]
        self.view.refresh(self.procesos)
        if hasattr(self.view, "reset_simulation"):
            self.view.reset_simulation()

    def run(self) -> None:
        self.root.mainloop()
        # Asegurar que los threads se cierren al salir
        self.ejecutando = False