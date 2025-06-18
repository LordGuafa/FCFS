import sys
import os

# Asegura que el directorio raíz del proyecto esté en sys.path
current_file_path: str = os.path.abspath(__file__)
project_root: str = os.path.dirname(current_file_path)  # Carpeta FCFS
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar el controlador desde la estructura MVC