import sys
import os

# Asegura que el directorio raíz del proyecto esté en sys.path
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)  # Carpeta FCFS
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar el controlador desde la estructura MVC
from controller.controller import Controller

if __name__ == "__main__":
    app = Controller()
    app.run()
