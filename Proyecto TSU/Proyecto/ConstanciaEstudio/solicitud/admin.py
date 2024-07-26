from django.contrib import admin
from .models import DataForm
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse

# Se llama al modelo para listar los datos que se obtendran
class DataFormAdmin(admin.ModelAdmin):
    list_display = ('p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'pnf', 'semestre', 'seccion', 'cedula', 'turno', 'creado_en',
                    'periodo_academico')
    
    #Se crea una variable llamada actions o accion para generar el pdf
    actions = ['generate_pdf']
    
    def generate_pdf(self, request, queryset): 
        # Una funcion donde toma los valores de la lista por su "id"
        dataform_id = queryset.values_list('id', flat=True)[0]
        
        # La respuesta HttpResponse llama a las funciones PDF gracias a Canvas
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ' attachment ; filename="constancia.pdf" '
        
        # Creas una variable que llama a canvas donde le asignas el tamaño de la pagina (carta)
        p = canvas.Canvas(response, pagesize=letter)
        
        margen = inch # Los margenes son por pulgadas
        ancho, alto = letter # ancho y alto de la pagina tipo carta
        
        # Aqui comienzas a llamar la clase del modelo para tomar por id los datos
        dataform = DataForm.objects.get(id=dataform_id)
        primer_nombre = dataform.p_nombre
        segundo_nombre = dataform.s_nombre
        primer_apellido = dataform.p_apellido
        segundo_apellido = dataform.s_apellido
        cedula = dataform.cedula
        edad = dataform.edad
        pnf = dataform.pnf
        seccion = dataform.seccion
        semestre = dataform.semestre
        turno = dataform.turno
        periodo = dataform.periodo_academico
        
        fecha = dataform.creado_en
        
        # Asignacion de tipo de letra y titulo del archivo PDF llamando a la variable {nombres}
        
        p.setTitle(f"Constancia de estudio {primer_nombre} {primer_apellido}")
        p.setFont('Times-Roman',12)
        # Variable imagen para poner el logo de la universidad, ubicando su carpeta y asignando el tamaño
        imagen = ImageReader("solicitud/static/images/Logo_Unexca.jpg")
        p.drawImage(imagen, 50, 730, width=50, height=50)
        
        # La variable texto se ubica el encabezado y la etiqueta <br/> sirve como salto de linea
        # Etiqueta que funciona en los archivos HTML
        texto = f"""REPUBLICA BOLIVARIANA DE VENEZUELA <br/>
                    MINISTERIO DEL PODER POPULAR PARA LA EDUCACION UNIVERSITARIA <br/>
                    UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS - UNEXCA"""
        
        # ParagraphStyle ayuda al interlineado del texto y posicionamiento
        estilo = ParagraphStyle(name="Normal", alignment=1, spaceBefore=0, spaceAfter=0, leading=18)
        
        # Con Paragraph permite seguir las posiciones del sistema cartesiano
        parrafo = Paragraph(texto,estilo)
        parrafo.wrapOn(p, ancho - 2 * margen, alto - 2 * margen) # El metodo wrapOn sirve para calcular el tamaño que ocuparia un texto
        parrafo.drawOn(p, margen, margen * 10) # El metodo drawOn escribe o dibuja el texto en PDF y se especifica la posicion y el ancho
        
        # Con este metodo permite calcular y centrar un String o texto y se calcula su posicion
        p.drawCentredString(ancho / 2, alto - 2 * margen, "CONSTANCIA DE ESTUDIOS")
        
        # Se crea una segunda variable llamada texto2 para poner la informacion acerca de la constancia de estudio y llama los datos
        # Que se encuentran en el modelo.
        
        texto2 = f"""Quien suscribe, Ing. Yovany Diaz, Jefe(E) Coordinacion Control de Estudios de la UNIVERSIDAD NACIONAL EXPERIMENTAL
        DE LA GRAN CARACAS, hace constar por medio la presente que el(la) ciudadano(na) {primer_apellido} {segundo_apellido} 
        {primer_nombre} {segundo_nombre}, titular de la cedula de identidad Nº {cedula}, es estudiante activo(a) de esta universidad en el nucleo Altagracia actualmente cursa 
        periodo academico {periodo}. del Programa Nacional de Formacion Informatica, {seccion}, {turno}. <br/> <br/>
        
        Constancia que se expide a peticion de la parte interesada en Caracas, {fecha}."""
        
        # Se repite el proceso de asignacion de posicion y alineacion
        estilo2 = ParagraphStyle(name="Normal", alignment=4, spaceBefore=0, spaceAfter=0, leading=18)
        parrafo2 = Paragraph(texto2, estilo2)
        
        parrafo2.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
        parrafo2.drawOn(p, margen, margen * 6)
        
        # Se hace un tercer texto que se encuentra al final del documento, en este caso no hubo necesidad de una posicion
        # sino que usa una posicion por defecto.
        
        texto3 = f"""Atentamente, <br/> <br/> <br/>
                    ING YOVANY DIAZ <br/>
                    JEFE(E) COORDINACION CONTROL DE ESTUDIOS  <br/>
                    NUCLEO-ALTAGRACIA"""
        
        # Estas variables permite calcular para hacer una linea.
        ancho2 = 8.5 * inch
        x1 = 50 # Posicion del eje x1
        x2 = 250 # Posicion del eje x2
        y = 270 # Posicion del eje y
        ancho_linea = x2 - x1
        x = (ancho2 - ancho_linea) / 2
        p.line(x, y, x + ancho_linea, y) # El metodo line dibuja una linea y te permite usar las variables de calculo
        
        # Se le asignan unos estilos igualmente a la variable de texto3
        estilo3 = ParagraphStyle(name="Normal", alignment=1, spaceBefore=0, spaceAfter=0, leading=18)
        
        parrafo3 = Paragraph(texto3,estilo3)
        
        # Se repite el proceso de la posicion del texto
        parrafo3.wrapOn(p, ancho - 2 * margen, alto - 2 * margen)
        parrafo3.drawOn(p, margen, margen * 3)
        
        p.showPage() # El metodo showPage() permite mostrar todo este contenido creado.
        p.save() # El metodo save() permite salvar todos los datos y funciones creadas.
        return response
    # Llamas a la funcion generate_pdf y con short_description te permite crear el boton donde descargaras el PDF desde un item.
    generate_pdf.short_description = "Descarga los items como PDF"



# Register your models here.
# Aqui registras los modelos de base de datos para que aparezcan en el panel de administracion.
admin.site.register(DataForm, DataFormAdmin)
