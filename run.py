from app import create_app
from download_model import descargar_modelo, descargar_yolov5 # type: ignore


# Descargas automáticas
descargar_modelo()
descargar_yolov5()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
