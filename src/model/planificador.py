from abc import ABC, abstractmethod
from collections import deque
from typing import List
from model.proceso import Proceso

class Planificador(ABC):
    def __init__(self) -> None:
        self.lista_procesos: deque[Proceso] = deque()
        self.observers = []

    def add_observer(self, observer) -> None:
        self.observers.append(observer)

    def notify_observers(self) -> None:
        for observer in self.observers:
            observer.update_from_model(self.get_procesos())

    def add_proceso(self, proceso: Proceso) -> None:
        self.lista_procesos.append(proceso)
        self.notify_observers()

    def get_procesos(self) -> List[Proceso]:
        return list(self.lista_procesos)

    @abstractmethod
    def run(self) -> List[Proceso]:
        """Ejecuta el algoritmo de planificación y retorna la lista de procesos ordenada"""
        pass

    def recalcular_tiempos(self, procesos: List[Proceso]) -> None:
        """Recalcula los tiempos de los procesos basado en el algoritmo específico"""
        self.lista_procesos = deque(iterable=procesos)
        resultado: List[Proceso] = self.run()
        for i, p in enumerate(iterable=procesos):
            p.tiempo_inicio = resultado[i].tiempo_inicio
            p.tiempo_final = resultado[i].tiempo_final
            p.tiempo_retorno = resultado[i].tiempo_retorno
            p.tiempo_espera = resultado[i].tiempo_espera
        self.notify_observers()
