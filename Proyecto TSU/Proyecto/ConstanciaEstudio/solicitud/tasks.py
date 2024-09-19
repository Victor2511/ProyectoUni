from django.core.mail import EmailMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from .models import Constancia
from django.conf import settings
import os

def generate_and_send_constancia(constancia_id):  # Solo recibe el ID de la constancia
    # Obtener la constancia
    constancia = Constancia.objects.get(id=constancia_id)
    estudiante = constancia.estudiante
    
    # Obtener los datos del estudiante
    primer_nombre = estudiante.p_nombre
    segundo_nombre = estudiante.s_nombre
    primer_apellido = estudiante.p_apellido
    segundo_apellido = estudiante.s_apellido
    cedula = estudiante.cedula
    correo = estudiante.correo
    pnf = estudiante.pnf
    seccion = estudiante.seccion
    turno = estudiante.turno
    periodo = estudiante.periodo_academico
    fecha = constancia.fecha_solicitud
    
    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="constancia - {primer_nombre}_{primer_apellido}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    margen = inch
    ancho, alto = letter

    # Dibujar el contenido del PDF
    p.setTitle(f"Constancia de estudio {primer_nombre} {primer_apellido}")
    p.setFont('Times-Roman', 12)
    
    image_path = os.path.join(settings.BASE_DIR, 'solicitud/static/css/images/Logo_Unexca.jpg')
    
    imagen = ImageReader(image_path)
    
    
    
    p.drawImage(imagen, 50, 730, width=50, height=50)
    
    texto = """REPUBLICA BOLIVARIANA DE VENEZUELA <br/>
                MINISTERIO DEL PODER POPULAR PARA LA EDUCACION UNIVERSITARIA <br/>
                UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS - UNEXCA"""
    
    estilo = ParagraphStyle(name="Normal", alignment=1, spaceBefore=0, spaceAfter=0, leading=18)
    
    parrafo = Paragraph(texto, estilo)
    parrafo.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
    parrafo.drawOn(p, margen, margen * 10)
    
    p.drawCentredString(ancho / 2, alto - 2 * margen, "CONSTANCIA DE ESTUDIOS")
    
    # Segundo bloque de texto
    texto2 = f"""Quien suscribe, Ing. Yovany Diaz, Jefe(E) Coordinacion Control de Estudios de la UNIVERSIDAD NACIONAL EXPERIMENTAL
        DE LA GRAN CARACAS, hace constar por medio la presente que el(la) ciudadano(a) {primer_apellido} {segundo_apellido} 
        {primer_nombre} {segundo_nombre}, titular de la cedula de identidad Nº {cedula}, es estudiante activo(a) de esta universidad en el nucleo Altagracia actualmente cursa 
        periodo academico {periodo}. del Programa Nacional de Formacion {pnf}, {seccion}, {turno}. <br/> <br/>
        
        Constancia que se expide a peticion de la parte interesada en Caracas, {fecha.strftime("%d/%m/%Y")}."""
        
    estilo2 = ParagraphStyle(name="Normal", alignment=4, spaceBefore=0, spaceAfter=0, leading=18)
    parrafo2 = Paragraph(texto2, estilo2)
    parrafo2.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
    parrafo2.drawOn(p, margen, margen * 6)
    texto3 = """Atentamente, <br/> <br/> <br/>
                    ING YOVANY DIAZ <br/>
                    JEFE(E) COORDINACION CONTROL DE ESTUDIOS  <br/>
                    NUCLEO-ALTAGRACIA"""
        
    ancho2 = 8.5 * inch
    x1 = 50
    x2 = 250
    y = 270
    ancho_linea = x2 - x1
    x = (ancho2 - ancho_linea) / 2
    p.line(x, y, x + ancho_linea, y)
    
    estilo3 = ParagraphStyle(name="Normal", alignment=1, spaceBefore=0, spaceAfter=0, leading=18)
    parrafo3 = Paragraph(texto3, estilo3)
    parrafo3.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
    parrafo3.drawOn(p, margen, margen * 3)
    
    p.showPage()
    p.save()

    # Enviar el correo electrónico con el PDF adjunto
    email = EmailMessage(
        'Constancia de Estudio solicitada',
        f'Hola {primer_nombre} {primer_apellido}, tu solicitud de constancia de estudio ha sido exitosa. '
        'Por favor revisa el archivo adjunto para obtener tu constancia de estudio.',
        'victorgabrieljunior@gmail.com',
        [correo]
    )
    email.attach(f'constancia_{primer_nombre}_{primer_apellido}.pdf', response.getvalue(), 'application/pdf')
    email.send(fail_silently=False)
