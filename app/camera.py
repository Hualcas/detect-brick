import base64
import cv2
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
import os
import sys





class VideoCamera:
    def __init__(self, camara_index=0):
        self.camera_index = camara_index
        self.running = False
        self.total_counts = {'fisura': 0, 'rotura': 0, 'bueno': 0}
        self.start_time = datetime.now()
        self.end_time = None
        self.tiempos_fisura = []

        # Compatibilidad Pathlib en Windows
        sys.modules['pathlib'].PosixPath = Path

        # Cargar modelo YOLO
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='best50e1.pt')
        self.model.conf = 0.5
        self.model.iou = 0.45
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(device)

        if os.environ.get("RENDER") != "true":
            self.video = cv2.VideoCapture(camara_index)
            if not self.video.isOpened():
                print(f"⚠️ No se pudo abrir la cámara con índice {camara_index}")
                self.video = None
        else:
            self.video = None

    def get_frame(self):
        if self.video is None or not self.video.isOpened():
            return None
        success, frame = self.video.read()
        return self._procesar_frame(frame) if success else None

    def procesar_frame_base64(self, base64_data: str):
        try:
            img_data = base64.b64decode(base64_data.split(',')[-1])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return self._procesar_frame(frame)
        except Exception as e:
            print(f"Error al procesar frame base64: {e}")
            return None

    def _procesar_frame(self, frame):
        self.counts = {'fisura': 0, 'rotura': 0, 'bueno': 0}
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(img, size=640)
        detections = results.xyxy[0]

        for *box, conf, cls in detections:
            label = self.model.names[int(cls)]
            if label in self.counts:
                self.counts[label] += 1
                self.total_counts[label] += 1
                if label == 'fisura':
                    self.tiempos_fisura.append((datetime.now() - self.start_time).total_seconds())
            x1, y1, x2, y2 = map(int, box)
            color = (0, 255, 0) if label == 'bueno' else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {float(conf):.1f}%", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        conteo = f"Fisuras: {self.counts['fisura']}  Roturas: {self.counts['rotura']}  Buenos: {self.counts['bueno']}"
        cv2.putText(frame, conteo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        self.precision = self.get_precision()
        return jpeg.tobytes()

    def get_precision(self):
        total = sum(self.total_counts.values())
        defectuosos = self.total_counts['fisura'] + self.total_counts['rotura']
        return round((defectuosos / total) * 100, 2) if total else 0.0

    def obtener_tiempo_promedio_fisura(self):
        return round(sum(self.tiempos_fisura) / len(self.tiempos_fisura), 2) if self.tiempos_fisura else 0.0

    def save_results(self):
        
        from fpdf import FPDF # type: ignore

        total = sum(self.total_counts.values())
        malos = self.total_counts['fisura'] + self.total_counts['rotura']
        buenos = self.total_counts['bueno']
        precision = self.get_precision()
        tiempo_promedio = self.obtener_tiempo_promedio_fisura()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Reporte de Monitoreo", ln=True, align='C')
        pdf.cell(200, 10, f"Inicio: {self.start_time}", ln=True)
        pdf.cell(200, 10, f"Fin: {self.end_time}", ln=True)
        pdf.cell(200, 10, f"Total ladrillos: {total}", ln=True)
        pdf.cell(200, 10, f"Buenos: {buenos}", ln=True)
        pdf.cell(200, 10, f"Malos: {malos}", ln=True)
        pdf.cell(200, 10, f"Precisión: {precision:.2f}%", ln=True)
        pdf.cell(200, 10, f"Tiempo promedio de fisura: {tiempo_promedio:.2f}s", ln=True)

        os.makedirs("reportes", exist_ok=True)
        filename = f"reporte_{self.start_time.strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(f"reportes/{filename}")

    def reset_counts(self):
        self.total_counts = {'fisura': 0, 'rotura': 0, 'bueno': 0}
        self.tiempos_fisura = []
        self.start_time = datetime.now()
        self.end_time = None

    def release(self):
        if self.video and self.video.isOpened():
            self.video.release()
        self.end_time = datetime.now()
        try:
            self.save_results()
        except Exception as e:
            print(f"❌ Error al guardar resultados: {e}")
