from collections import deque
from model.planificador import Planificador
from model.proceso import Proceso
from typing import List

class FCFS(Planificador):

    def __init__(self) -> None:
        super().__init__()
        self.lista_procesos: deque[Proceso] = deque()


    def add_proceso(self, proceso:Proceso) -> None:
        self.lista_procesos.append(proceso)

    def run(self) -> List[Proceso]:
        """
        Implementa el algoritmo First-Come-First-Serve
        """
        retorno: List[Proceso] = []
        tiempo_actual = 0

        # Ordenar procesos por tiempo de llegada
        procesos_ordenados: List[Proceso] = sorted(self.lista_procesos, key=lambda x: x.tiempo_llegada)

        for proceso in procesos_ordenados:
            proceso.tiempo_inicio = max(tiempo_actual, proceso.tiempo_llegada)
            proceso.tiempo_final = proceso.tiempo_inicio + proceso.rafaga
            proceso.tiempo_retorno = proceso.tiempo_final - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.rafaga
            tiempo_actual = proceso.tiempo_final
            retorno.append(proceso)

        return retorno

    def recalcular_tiempos(self, procesos: list[Proceso]) -> None:
        tiempo_actual = 0
        for proceso in procesos:
            proceso.tiempo_inicio = max(tiempo_actual, proceso.tiempo_llegada)
            proceso.tiempo_final = proceso.tiempo_inicio + proceso.rafaga
            proceso.tiempo_retorno = proceso.tiempo_final - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.rafaga
            tiempo_actual = proceso.tiempo_final