from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os

from Menu.models import Documentos, student_registration

def generate_and_send_carnet_sync(estudiante_id):
    try:
        # Obtener el estudiante
        estudiante = student_registration.objects.get(id=estudiante_id)

        # Buscar la foto del carnet
        foto_carnet = Documentos.objects.filter(
            estudiante=estudiante, 
            tipo_documento=Documentos.FOTO_CARNET
            ).first()
        foto_path = os.path.join(settings.MEDIA_ROOT, str(foto_carnet.archivo)) if foto_carnet else None

        # Datos del estudiante
        nombre = f"{estudiante.p_nombre} {estudiante.s_nombre} {estudiante.p_apellido} {estudiante.s_apellido}"
        cedula = estudiante.cedula
        pnf = estudiante.pnf
        seccion = estudiante.seccion
        turno = estudiante.turno

        # Ruta temporal para el PDF
        pdf_filename = f"carnet_{estudiante.p_nombre}_{estudiante.p_apellido}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, "carnets", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # Crear el PDF
        p = canvas.Canvas(pdf_path, pagesize=letter)
        ancho, alto = letter

        # Agregar fondo de color
        p.setFillColorRGB(0.2, 0.6, 0.8)  # Azul oscuro
        p.rect(0, 0, ancho, alto, fill=True, stroke=False)

        # Encabezado
        p.setFillColorRGB(1, 1, 1)  # Blanco
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(ancho / 2, alto - 80, "UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS")
        p.setFont("Helvetica", 14)
        p.drawCentredString(ancho / 2, alto - 100, "Carnet Estudiantil")

        # Foto del estudiante
        if foto_path and os.path.exists(foto_path):
            p.drawImage(ImageReader(foto_path), ancho - 170, alto - 250, width=120, height=140)
        else:
            p.setFillColorRGB(1, 0, 0)  # Rojo para indicar error
            p.drawString(ancho - 170, alto - 250, "FOTO NO DISPONIBLE")

        # Información del estudiante
        p.setFillColorRGB(1, 1, 1)  # Blanco
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, alto - 180, "Nombre:")
        p.setFont("Helvetica", 12)
        p.drawString(120, alto - 180, nombre)

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, alto - 200, "Cédula:")
        p.setFont("Helvetica", 12)
        p.drawString(120, alto - 200, str(cedula))

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, alto - 220, "PNF:")
        p.setFont("Helvetica", 12)
        p.drawString(120, alto - 220, str(pnf))

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, alto - 240, "Sección:")
        p.setFont("Helvetica", 12)
        p.drawString(120, alto - 240, str(seccion))

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, alto - 260, "Turno:")
        p.setFont("Helvetica", 12)
        p.drawString(120, alto - 260, str(turno))

        # Guardar PDF
        p.showPage()
        p.save()

        # Enviar el carnet por correo
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

def send_email_task(subject, message, recipient_list):
    """
    Tarea asíncrona para enviar correos electrónicos.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Usa el email configurado en settings.py
        recipient_list,
        fail_silently=False,
    )
