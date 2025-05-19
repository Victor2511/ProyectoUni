import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def procesar_foto_carnet(image_file):
    # Cargar imagen en formato OpenCV desde InMemoryUploadedFile
    img_array = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # Convertir a escala de grises para detección de rostro
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Cargar clasificador pre-entrenado Haar Cascade para rostro
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        raise ValueError("No se detectó ningún rostro en la imagen")

    # Tomamos el primer rostro detectado
    (x, y, w, h) = faces[0]

    # Añadir margen para que no esté tan recortado
    margin = int(h * 0.5)
    x1 = max(x - margin, 0)
    y1 = max(y - margin, 0)
    x2 = min(x + w + margin, img.shape[1])
    y2 = min(y + h + margin, img.shape[0])

    # Recortar la imagen alrededor del rostro
    face_crop = img[y1:y2, x1:x2]

    # Eliminar fondo (simplificado): detectar fondo por color dominante en esquinas
    mask = np.zeros(face_crop.shape[:2], np.uint8)
    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)

    rect = (10, 10, face_crop.shape[1] - 20, face_crop.shape[0] - 20)
    cv2.grabCut(face_crop, mask, rect, bg_model, fg_model, 5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    face_clean = face_crop * mask2[:, :, np.newaxis]

    # Crear fondo blanco
    background = np.ones_like(face_crop, np.uint8) * 255
    final = background.copy()
    final[mask2 == 1] = face_crop[mask2 == 1]

    # Redimensionar a tamaño tipo carnet (por ejemplo 300x400 píxeles)
    carnet_img = cv2.resize(final, (300, 400))

    # Convertir a JPEG para guardar
    _, jpeg = cv2.imencode('.jpg', carnet_img)
    processed_image = ContentFile(jpeg.tobytes(), name='foto_carnet.jpg')

    return processed_image
