# download_model.py
import gdown # type: ignore
import os
import subprocess

def descargar_modelo():
    # Descargar modelo desde Google Drive
    url = 'https://drive.google.com/uc?id=174Td9kRd10iImunxIwrXZsKn9PduBDTX'
    output = 'best50e1.pt'
    if not os.path.exists(output):
        print("📥 Descargando modelo desde Google Drive...")
        gdown.download(url, output, quiet=False)
    else:
        print("✅ El modelo ya existe, no se descargará de nuevo.")

def clonar_yolov5():
    if not os.path.exists('yolov5'):
        print("📥 Clonando repositorio YOLOv5 desde GitHub...")
        subprocess.run(['git', 'clone', 'https://github.com/ultralytics/yolov5.git'])
    else:
        print("✅ YOLOv5 ya está clonado.")

def setup_entorno():
    
    clonar_yolov5()
    descargar_modelo()

if __name__ == '__main__':
    setup_entorno()
