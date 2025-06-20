import logging
import os
from datetime import datetime

def setup_logger():
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Configurar el nombre del archivo de log con la fecha actual
    log_file = os.path.join(log_dir, f'fcfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configurar el logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
