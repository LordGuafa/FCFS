from typing import List
from model.planificador import Planificador
from model.proceso import Proceso

class Prioridades(Planificador):
    def run(self) -> List[Proceso]:
        # Solo considerar procesos con prioridad válida y que no han terminado
        procesos = [p for p in self.lista_procesos if p.prioridad is not None and p.tiempo_final == 0]
        # Obtener el tiempo final más alto de los procesos ya ejecutados
        procesos_ya_ejecutados = [p for p in self.lista_procesos if p.tiempo_final > 0]
        if procesos_ya_ejecutados:
            tiempo_actual = max(p.tiempo_final for p in procesos_ya_ejecutados)
        else:
            tiempo_actual = 0
        retorno = []

        # Ordenar por llegada y prioridad
        procesos.sort(key=lambda p: (p.tiempo_llegada, p.prioridad))

        while procesos:
            disponibles: List[Proceso] = [p for p in procesos if p.tiempo_llegada <= tiempo_actual]
            if not disponibles:
                tiempo_actual += 1
                continue

            siguiente = min(disponibles, key=lambda p: p.prioridad) # type: ignore
            procesos.remove(siguiente)

            siguiente.tiempo_inicio = max(tiempo_actual, siguiente.tiempo_llegada)
            siguiente.tiempo_final = siguiente.tiempo_inicio + siguiente.rafaga
            siguiente.tiempo_espera = siguiente.tiempo_inicio - siguiente.tiempo_llegada
            siguiente.tiempo_retorno = siguiente.tiempo_final - siguiente.tiempo_llegada

            retorno.append(siguiente)
            tiempo_actual = siguiente.tiempo_final
            print(f"Proceso {siguiente.nombre} ejecutado: Inicio={siguiente.tiempo_inicio}, Final={siguiente.tiempo_final}, Retorno={siguiente.tiempo_retorno}, Espera={siguiente.tiempo_espera}")
        return retorno