# utils.py
import os
from pathlib import Path
import sys
from PIL import Image
from io import BytesIO
import torch
from ultralytics.yolo.engine.model import YOLO # type: ignore
from yolov5.models.common import DetectMultiBackend  # type: ignore # Asegúrate de tener yolov5 como submódulo o instalación

# ⚠️ Asegura que 'best50e1.pt' se haya descargado previamente
MODEL_PATH = 'best50e1.pt'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ✅ Usa DetectMultiBackend
modelo = DetectMultiBackend(MODEL_PATH, device=device, dnn=False)
modelo.model.float()
modelo.model.eval()
modelo.warmup(imgsz=(1, 3, 640, 640))

def procesar_imagen(frame_array):
    import numpy as np
    import torchvision.transforms as transforms

    # Preprocesamiento
    img = Image.fromarray(frame_array).convert('RGB')
    img = np.array(img)

    im = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float().to(device) / 255.0

    pred = modelo(im)[0]

    # Filtrar predicciones por confianza
    conf_thres = 0.5
    pred = pred[pred[:, 4] > conf_thres]

    nombres = modelo.names
    clases_detectadas = [nombres[int(cls)] for cls in pred[:, 5]]

    return clases_detectadas
