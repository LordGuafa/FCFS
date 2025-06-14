class Proceso:
    def __init__(self, nombre: str, TA: int, R: int,)-> None:
        """_summary_

        Args:
            nombre (str): nombre del proceso
            TA (int): Tiempo de llegada
            R (int): Tiempo de duración (ráfaga)
            TI (int): Tiempo de inicio
            TF (int): Tiempo de finalización
            TR (int): Tiempo de retorno
            TE (int): Tiempo de espera
        """
        self.nombre = nombre
        self.TA: int = TA # Tiempo de llegada
        self.R: int = R #
        self.TI: int = 0
        self.TF: int = 0
        self.TR: int = 0
        self.TE : int= 0




