class Proceso:
    def __init__(self, nombre: str, tiempo_llegada: int, rafaga: int,algoritmo:str, prioridad: int | None = None) -> None:
        """_summary_

        Args:
            nombre (str): nombre del proceso
            tiempo_llegada (int): Tiempo de llegada
            rafaga (int): Tiempo de duración (ráfaga)
            prioridad (int, opcional): Prioridad del proceso (menor valor = mayor prioridad)
        """
        self.nombre: str = nombre
        self.tiempo_llegada: int = tiempo_llegada # Tiempo de llegada
        self.rafaga: int = rafaga #
        self.tiempo_inicio: int = 0
        self.tiempo_final: int = 0
        self.tiempo_retorno: int = 0
        self.tiempo_espera : int= 0
        self.prioridad: int | None = prioridad  # Puede ser None si no aplica
        self.algoritmo: str = algoritmo




