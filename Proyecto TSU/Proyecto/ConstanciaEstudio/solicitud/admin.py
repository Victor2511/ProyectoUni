from django.contrib import admin
from .models import Constancia
from django_q.tasks import async_task
from .tasks import generate_and_send_constancia

""" Actualizacion: para el panel de administracion creamos una clase que permite ordenar y obtener los datos de
student_registration anteriormente referenciados, pero para no complicarnos en como apareceran los nombres
creamos unas funciones personalizadas que sirven tanto para asignar nombres cortos y tener un modo de filtrar por datos """

class ConstanciaAdmin(admin.ModelAdmin):
    list_display = ('get_nombre', 'get_apellido', 'get_cedula', 'get_email', 'get_fecha_solicitud', 'estado', 'primera_solicitud')
    
    
    
    def get_nombre(self, obj):
        try:
            return obj.estudiante.p_nombre
        except AttributeError:
            return "Nombre no disponible"
    get_nombre.short_description = 'Nombre' # short_description sirve para agregar un nombre corto y personalizado y no se vea tal cual como el campo.
    
    
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
    get_cedula.admin_order_field = 'estudiante__cedula' # admin_order_field sirve para filtrar
    
    
    def get_email(self, obj):
        try:
            return obj.estudiante.correo
        except AttributeError:
            return "Correo no disponible"
    get_email.short_description = 'Correo Electronico'
    
    def get_fecha_solicitud(self, obj):
        return obj.fecha_solicitud
    get_fecha_solicitud.short_description = 'Fecha de Solicitud'
    
    
    
    actions = ['generate_pdf_async']
    
    def generate_pdf_async(self, request, queryset):
        constancia_id = queryset.values_list('id', flat=True)[0]
        
        # Llamar a la tarea asíncrona para generar y enviar la constancia
        async_task('solicitud.tasks.generate_and_send_constancia', constancia_id)
        
        self.message_user(request, "La constancia se está generando y enviando por correo de forma asíncrona.")
    
    generate_pdf_async.short_description = "Generar constancia y enviarla por correo (asíncrono)"

admin.site.register(Constancia, ConstanciaAdmin)

