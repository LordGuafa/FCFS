from collections import deque
from model.planificador import Planificador
from model.proceso import Proceso
from typing import List

class FCFS(Planificador):

    def __init__(self) -> None:
        super().__init__()
        self.tiempo_inicial: int = 0  # Para soportar ejecución dinámica

    def add_proceso(self, proceso: Proceso) -> None:
        self.lista_procesos.append(proceso)

    def run(self) -> List[Proceso]:
        """
        Implementa el algoritmo First-Come-First-Serve con soporte para ejecución dinámica.
        Los procesos se ejecutan en el orden en que fueron agregados, no por tiempo de llegada.
        """
        retorno: List[Proceso] = []
        tiempo_actual = max(self.tiempo_inicial, 0)

        # NO ordenar, usar el orden de self.lista_procesos
        for proceso in self.lista_procesos:
            proceso.tiempo_inicio = max(
                tiempo_actual, 
                proceso.tiempo_llegada, 
                self.tiempo_inicial
            )
            proceso.tiempo_final = proceso.tiempo_inicio + proceso.rafaga
            proceso.tiempo_retorno = proceso.tiempo_final - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.rafaga

            tiempo_actual = proceso.tiempo_final
            retorno.append(proceso)

        return retorno

    def recalcular_tiempos(self, procesos: List[Proceso]) -> None:
        """Recalcula los tiempos considerando el tiempo actual de simulación"""
        tiempo_actual = self.tiempo_inicial

        # NO ordenar, usar el orden de la lista recibida
        for proceso in procesos:
            proceso.tiempo_inicio = max(tiempo_actual, proceso.tiempo_llegada, self.tiempo_inicial)
            proceso.tiempo_final = proceso.tiempo_inicio + proceso.rafaga
            proceso.tiempo_retorno = proceso.tiempo_final - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.rafaga
            tiempo_actual = proceso.tiempo_final

    def get_procesos_activos(self, tiempo_actual: int) -> List[Proceso]:
        """Retorna los procesos que están activos en el tiempo dado"""
        return [
            p for p in self.lista_procesos 
            if p.tiempo_inicio <= tiempo_actual < p.tiempo_final
        ]

    def get_procesos_pendientes(self, tiempo_actual: int) -> List[Proceso]:
        """Retorna los procesos que aún no han comenzado"""
        return [
            p for p in self.lista_procesos 
            if p.tiempo_inicio > tiempo_actual or p.tiempo_final == 0
        ]