class Proceso:
    def __init__(self, nombre: str, TA: float, R: float,)-> None:
        """_summary_

        Args:
            nombre (str): nombre del proceso
            TA (float): Tiempo de llegada
            R (float): Tiempo de duración (ráfaga)
            TI (float): Tiempo de inicio
            TF (float): Tiempo de finalización
            TR (float): Tiempo de retorno
            TE (float): Tiempo de espera
        """
        self.nombre = nombre
        self.TA: float = TA # Tiempo de llegada
        self.R: float = R #
        self.TI: float = 0
        self.TF: float = 0
        self.TR: float = 0
        self.TE : float= 0




