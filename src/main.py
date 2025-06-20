import sys
import os

# Asegura que el directorio raíz del proyecto esté en sys.path
current_file_path: str = os.path.abspath(__file__)
project_root: str = os.path.dirname(current_file_path)  # Carpeta FCFS
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar el controlador y el logger
from controller.controller import Controller
from utils.logger import setup_logger

if __name__ == "__main__":
    # Configurar el logger
    logger = setup_logger()
    logger.info("Iniciando aplicación FCFS")
    
    try:
        app = Controller()
        logger.info("Controlador iniciado correctamente")
        app.run()
        logger.info("Aplicación finalizada correctamente")
    except Exception as e:
        logger.error(f"Error en la aplicación: {str(e)}")
        sys.exit(1)