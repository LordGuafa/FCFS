from typing import List
from model.planificador import Planificador
from model.proceso import Proceso

class Prioridades(Planificador):
    def __init__(self) -> None:
        super().__init__()
        self.tiempo_inicial: int = 0  # Para soportar ejecución dinámica

    def run(self) -> List[Proceso]:
        """
        Implementa el algoritmo de Prioridades con soporte para ejecución dinámica
        """
        # Filtrar procesos válidos
        procesos = [
            p for p in self.lista_procesos 
            if p.prioridad is not None
        ]
        
        if not procesos:
            return []

        tiempo_actual = max(self.tiempo_inicial, 0)
        retorno = []
        procesos_pendientes = procesos.copy()

        # Ordenar inicialmente por tiempo de llegada para procesamiento
        procesos_pendientes.sort(key=lambda p: p.tiempo_llegada)

        while procesos_pendientes:
            # Encontrar procesos que ya han llegado
            disponibles: List[Proceso] = [
                p for p in procesos_pendientes 
                if p.tiempo_llegada <= tiempo_actual
            ]
            
            if not disponibles:
                # Si no hay procesos disponibles, avanzar al siguiente tiempo de llegada
                tiempo_actual = min(p.tiempo_llegada for p in procesos_pendientes)
                continue

            # Seleccionar el proceso con mayor prioridad (menor número = mayor prioridad)
            siguiente = min(disponibles, key=lambda p: (p.prioridad, p.tiempo_llegada))
            procesos_pendientes.remove(siguiente)

            # Calcular tiempos
            siguiente.tiempo_inicio = max(tiempo_actual, siguiente.tiempo_llegada, self.tiempo_inicial)
            siguiente.tiempo_final = siguiente.tiempo_inicio + siguiente.rafaga
            siguiente.tiempo_espera = siguiente.tiempo_inicio - siguiente.tiempo_llegada
            siguiente.tiempo_retorno = siguiente.tiempo_final - siguiente.tiempo_llegada

            retorno.append(siguiente)
            tiempo_actual = siguiente.tiempo_final
            
            # Debug para seguimiento
            print(f"[Prioridades] Proceso {siguiente.nombre} ejecutado:")
            print(f"  Prioridad: {siguiente.prioridad}")
            print(f"  Inicio: {siguiente.tiempo_inicio}, Final: {siguiente.tiempo_final}")
            print(f"  Retorno: {siguiente.tiempo_retorno}, Espera: {siguiente.tiempo_espera}")

        return retorno

    def recalcular_tiempos(self, procesos: List[Proceso], tiempo_actual: int = 0) -> None:
        """Recalcula los tiempos desde un punto específico en el tiempo"""
        self.tiempo_inicial = tiempo_actual
        self.lista_procesos.clear()
        
        for proceso in procesos:
            if proceso.prioridad is not None:
                # Resetear proceso si no ha comenzado o está en progreso
                if proceso.tiempo_inicio >= tiempo_actual:
                    proceso.tiempo_inicio = 0
                    proceso.tiempo_final = 0
                    proceso.tiempo_retorno = 0
                    proceso.tiempo_espera = 0
                self.add_proceso(proceso)
        
        # Ejecutar algoritmo
        resultado = self.run()
        
        # Actualizar procesos originales
        for i, proceso_resultado in enumerate(resultado):
            for proceso_original in procesos:
                if proceso_original.nombre == proceso_resultado.nombre:
                    proceso_original.tiempo_inicio = proceso_resultado.tiempo_inicio
                    proceso_original.tiempo_final = proceso_resultado.tiempo_final
                    proceso_original.tiempo_retorno = proceso_resultado.tiempo_retorno
                    proceso_original.tiempo_espera = proceso_resultado.tiempo_espera
                    break

    def get_proceso_actual(self, tiempo_actual: int) -> Proceso | None:
        """Retorna el proceso que debería estar ejecutándose en el tiempo dado"""
        for proceso in self.lista_procesos:
            if proceso.tiempo_inicio <= tiempo_actual < proceso.tiempo_final:
                return proceso
        return None

    def puede_ser_interrumpido(self, proceso_actual: Proceso, nuevo_proceso: Proceso) -> bool:
        """
        Determina si el proceso actual puede ser interrumpido por uno nuevo
        En este caso, implementamos prioridades no expulsivas, pero se puede modificar
        """
        # Prioridades no expulsivas: el proceso actual no puede ser interrumpido
        return False
        
        # Para prioridades expulsivas, descomentar la línea siguiente:
        # return nuevo_proceso.prioridad < proceso_actual.prioridad