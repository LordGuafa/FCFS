from collections import deque
from model.proceso import Proceso

class FCFS:

    def __init__(self):
        self.lista_procesos: deque[Proceso] = deque()


    def add_proceso(self, proceso:Proceso) -> None:
        self.lista_procesos.append(proceso)

    def run(self) -> list[Proceso]:

        retorno:list[Proceso] = []
        tiempo_actual = 0
        for proceso in self.lista_procesos:
            proceso.TI = max(tiempo_actual, proceso.TA)
            proceso.TF = proceso.TI + proceso.R
            proceso.TR = proceso.TF - proceso.TA
            proceso.TE = proceso.TR - proceso.R
            tiempo_actual = proceso.TF
            retorno.append(proceso)

        return retorno