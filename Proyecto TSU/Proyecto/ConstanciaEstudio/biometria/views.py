from Menu.models import student_registration, Documentos
from django.core.files.base import ContentFile
import base64
import uuid

def guardar_foto_carnet_procesada(estudiante_id, imagen_procesada):
    """
    Guarda una imagen procesada como tipo 'Foto Carnet' en el modelo Documentos.

    Args:
        estudiante_id: ID del estudiante (clave primaria).
        imagen_procesada: imagen tipo PIL.Image ya procesada.
    """
    from io import BytesIO
    buffer = BytesIO()
    imagen_procesada.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    estudiante = student_registration.objects.get(id=estudiante_id)

    # Nombre único para el archivo
    nombre_archivo = f"foto_carnet_{uuid.uuid4().hex}.jpg"
    documento = Documentos.objects.create(
        estudiante=estudiante,
        tipo_documento=Documentos.FOTO_CARNET,
        archivo=ContentFile(image_bytes, name=nombre_archivo)
    )
    return documento
