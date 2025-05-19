from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import portrait
import os
from django.core.mail import send_mail
from Menu.models import Documentos, student_registration
import math

def generate_and_send_carnet_sync(estudiante_id):
    try:
        estudiante = student_registration.objects.get(id=estudiante_id)

        foto_carnet = Documentos.objects.filter(
            estudiante=estudiante, 
            tipo_documento=Documentos.FOTO_CARNET
        ).first()
        foto_path = os.path.join(settings.MEDIA_ROOT, str(foto_carnet.archivo)) if foto_carnet else None

        nombre = f"{estudiante.p_nombre} {estudiante.p_apellido}"
        cedula = estudiante.cedula
        pnf = estudiante.pnf
        seccion = estudiante.seccion
        semestre = getattr(estudiante, 'semestre', 'N/A')

        # Tamaño personalizado estilo tarjeta vertical (proporción similar a la imagen)
        width, height = 300, 500  # Ajustado a proporciones del carnet en la imagen

        pdf_filename = f"carnet_{estudiante.p_nombre}_{estudiante.p_apellido}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, "carnets", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        p = canvas.Canvas(pdf_path, pagesize=(width, height))

        # Fondo blanco
        p.setFillColorRGB(1, 1, 1)
        p.rect(0, 0, width, height, fill=1, stroke=0)

        # Header azul UNEXCA - Azul brillante como en la imagen
        p.setFillColor(HexColor("#0052CC"))  # Azul similar al de la imagen
        p.rect(0, height - 100, width, 100, fill=1, stroke=0)

        # Curva superior - ahora apuntando hacia arriba
        draw_wave(p, 0, height-130, width, 30, False, "#0052CC")

        # Logo UNEXCA
        logo_path = os.path.join(settings.BASE_DIR, 'Menu\static\css\images\logo_unexca_white.png')
        if os.path.exists(logo_path):
            p.drawImage(logo_path, 20, height - 80, width=60, height=60, mask='auto')
        

        # Área para la foto (cuadrada en lugar de circular)
        center_x = width / 2
        photo_size = 100  # Tamaño del cuadrado de la foto
        photo_y = height - 180
        
        # Coordenadas del cuadrado
        photo_x_start = center_x - photo_size/2
        photo_y_start = photo_y - photo_size/2
        
        # Dibujamos primero un fondo gris cuadrado
        p.setFillColor(HexColor("#888888"))
        p.rect(photo_x_start, photo_y_start, photo_size, photo_size, fill=1, stroke=0)
        
        if foto_path and os.path.exists(foto_path):
            # Para la foto cuadrada, simplemente la insertamos en el rectángulo
            p.drawImage(ImageReader(foto_path), 
                       photo_x_start, photo_y_start, 
                       width=photo_size, height=photo_size, mask='auto')
        else:
            # Dibujamos la silueta de persona en blanco sobre el fondo gris
            draw_person_silhouette(p, center_x, photo_y, photo_size/2)

        # Datos personales con estilo similar a la imagen
        p.setFillColor(HexColor("#3366CC"))  # Azul para el texto como en la imagen
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width / 2, height - 250, nombre.upper())

        p.setFont("Helvetica", 14)
        p.drawCentredString(width / 2, height - 280, f"C.I:{cedula}")
        p.drawCentredString(width / 2, height - 300, f"SEMESTRE:{semestre}")

        # Barra azul para PNF - Movida más abajo (30 unidades)
        p.setFillColor(HexColor("#0052CC"))
        p.rect(0, height - 350, width, 30, fill=1, stroke=0)
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 340, f"PNF: {pnf}")

        # Ola en la parte inferior - ahora apuntando hacia abajo
        draw_wave(p, 0, 0, width, 60, True, "#0052CC")

        # Vencimiento
        p.setFont("Helvetica", 9)
        p.setFillColorRGB(1, 1, 1)
        p.drawString(20, 10, "VENCIMIENTO: FEBRERO 2025")

        # Guardar PDF
        p.showPage()
        p.save()

        # Enviar por correo
        email = EmailMessage(
            'Carnet Estudiantil',
            f'Hola {estudiante.p_nombre} {estudiante.p_apellido}, adjunto encontrarás tu carnet estudiantil en formato PDF.',
            settings.DEFAULT_FROM_EMAIL,
            [estudiante.correo]
        )
        with open(pdf_path, 'rb') as pdf_file:
            email.attach(pdf_filename, pdf_file.read(), 'application/pdf')
        email.send(fail_silently=False)

        return f"Carnet generado y enviado con éxito a {estudiante.correo}"

    except student_registration.DoesNotExist:
        return "Error: El estudiante no existe."
    except Exception as e:
        return f"Error en la generación/envío del carnet: {e}"


def draw_clip_circle(canvas, x, y, radius):
    """Crea un clip circular para recortar imágenes en forma circular"""
    p = canvas.beginPath()
    p.circle(x, y, radius)
    canvas.clipPath(p)


def draw_person_silhouette(p, x, y, radius):
    """Dibuja una silueta simple de persona en el placeholder de la foto"""
    p.setFillColorRGB(1, 1, 1)
    
    # Cabeza
    head_radius = radius * 0.3
    p.circle(x, y + radius * 0.2, head_radius, fill=1, stroke=0)
    
    # Cuerpo
    p.setFillColorRGB(1, 1, 1)
    p.ellipse(x - radius * 0.4, y - radius * 0.5, x + radius * 0.4, y - radius * 0.1, fill=1, stroke=0)


def draw_wave(canvas, x, y, width, height, inverted=False, color="#0052CC"):
    """
    Dibuja una onda suave.
    Si inverted=True: la curva apunta hacia abajo (cóncava)
    Si inverted=False: la curva apunta hacia arriba (convexa)
    """
    canvas.saveState()
    
    # Configurar color
    canvas.setFillColor(HexColor(color))
    canvas.setStrokeColor(HexColor(color))
    
    # Dibujar la curva
    p = canvas.beginPath()
    
    # Parámetros para la curva
    amplitude = height * 0.8
    
    if inverted:
        # Curva apuntando hacia abajo (cóncava)
        p.moveTo(x, y)
        p.lineTo(x, y + height)
        p.curveTo(x + width/4, y + height - amplitude/2, 
                 x + width*3/4, y + height - amplitude, 
                 x + width, y + height)
        p.lineTo(x + width, y)
        p.close()
    else:
        # Curva apuntando hacia arriba (convexa)
        p.moveTo(x, y + height)
        p.lineTo(x, y)
        p.curveTo(x + width/4, y + amplitude/2, 
                 x + width*3/4, y + amplitude, 
                 x + width, y)
        p.lineTo(x + width, y + height)
        p.close()
    
    canvas.drawPath(p, fill=1, stroke=0)
    canvas.restoreState()
