from django.contrib import admin
from .models import Constancia
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse
from django.core.mail import EmailMessage


class ConstanciaAdmin(admin.ModelAdmin):
    list_display = ('get_nombre', 'get_apellido', 'get_cedula', 'get_email', 'get_fecha_solicitud', 'estado', 'primera_solicitud')
    
    
    
    def get_nombre(self, obj):
        try:
            return obj.estudiante.p_nombre
        except AttributeError:
            return "Nombre no disponible"
    get_nombre.short_description = 'Nombre'
    
    
    def get_apellido(self, obj):
        try:
            return obj.estudiante.p_apellido
        except AttributeError:
            return 'Apellido no disponible'
    get_apellido.short_description = 'Apellido'
    
    
    def get_cedula(self, obj):
        try:
            return obj.estudiante.cedula
        except AttributeError:
            return "Cedula no disponible"
    get_cedula.short_description = 'Cedula'
    get_cedula.admin_order_field = 'estudiante__cedula'
    
    
    def get_email(self, obj):
        try:
            return obj.estudiante.correo
        except AttributeError:
            return "Correo no disponible"
    get_email.short_description = 'Correo Electronico'
    
    def get_fecha_solicitud(self, obj):
        return obj.fecha_solicitud
    get_fecha_solicitud.short_description = 'Fecha de Solicitud'
    
    
    
    actions = ['generate_pdf']
    
    def generate_pdf(self, request, queryset): 
        constancia_id = queryset.values_list('id', flat=True)[0]
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="constancia.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        
        margen = inch
        ancho, alto = letter
        
        constancia = Constancia.objects.get(id=constancia_id)
        estudiante = constancia.estudiante
        primer_nombre = estudiante.p_nombre
        segundo_nombre = estudiante.s_nombre
        primer_apellido = estudiante.p_apellido
        segundo_apellido = estudiante.s_apellido
        cedula = estudiante.cedula
        correo = estudiante.correo
        edad = estudiante.edad
        pnf = estudiante.pnf
        seccion = estudiante.seccion
        semestre = estudiante.semestre
        turno = estudiante.turno
        periodo = estudiante.periodo_academico
        
        fecha = constancia.fecha_solicitud
        
        p.setTitle(f"Constancia de estudio {primer_nombre} {primer_apellido}")
        p.setFont('Times-Roman', 12)
        
        imagen = ImageReader("solicitud/static/images/Logo_Unexca.jpg")
        p.drawImage(imagen, 50, 730, width=50, height=50)
        
        texto = """REPUBLICA BOLIVARIANA DE VENEZUELA <br/>
                MINISTERIO DEL PODER POPULAR PARA LA EDUCACION UNIVERSITARIA <br/>
                UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS - UNEXCA"""
        
        estilo = ParagraphStyle(name="Normal", alignment=1, spaceBefore=0, spaceAfter=0, leading=18)
        
        parrafo = Paragraph(texto, estilo)
        parrafo.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
        parrafo.drawOn(p, margen, margen * 10)
        
        p.drawCentredString(ancho / 2, alto - 2 * margen, "CONSTANCIA DE ESTUDIOS")
        
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
        
        email = EmailMessage(
            'Constancia de Estudio solicitada',
            f'Hola {primer_nombre} {primer_apellido}, tu solicitud de constancia de estudio ha sido exitosa. '
            'Por favor revisa el archivo adjunto para obtener tu constancia de estudio.',
            'victorgabrieljunior@gmail.com',
            [correo]
        )
        email.attach(f'constancia_{primer_nombre}_{primer_apellido}.pdf', response.getvalue(), 'application/pdf')
        email.send(fail_silently=False)
        
        self.message_user(request, "Constancia generada y enviada por correo exitosamente.")
        
        # Esta procesando muy lento generar y enviar por correo la constancia y el mensaje retorna al
        # reiniciar la pagina. Tomar en cuenta
        
        return response
    
    generate_pdf.short_description = "Descarga los items como PDF"

admin.site.register(Constancia, ConstanciaAdmin)

