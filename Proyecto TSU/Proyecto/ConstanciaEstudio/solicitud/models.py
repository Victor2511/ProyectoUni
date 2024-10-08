from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Menu.models import student_registration
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

# Create your models here.
"""Se crea un modelo de base de datos para trabajar la informacion requerida
para generar la constancia de estudio, toda esta informacion es necesaria y se puede actualizar y migrar
a la base de datos que se utilice"""


# La clase Constancia permite crear un modelo de BDD para la solicitud de informacion a un estudiante.
# Estos datos navegaran hasta el admin.py que requiere esta informacion para generar la constancia de estudio.

""" Actualizacion: La nueva tabla Constancia hace referencia a student_registration mediante la variable estudiante
tiene una nueva variable que habla acerca del estado de la solicitud de la constancia y una tabla de tipo boolean
para validar de forma de checkbox si el estudiante es primera vez(o no) que solicita la constancia. """
class Constancia(models.Model):
    estudiante = models.ForeignKey(student_registration, on_delete=models.CASCADE, related_name='solicitudes')
    fecha_solicitud = models.DateTimeField(default=timezone.now, verbose_name='Fecha de solicitud')
    primera_solicitud = models.BooleanField(default=False, verbose_name='¿Primera Solicitud?')
    estado = models.CharField(max_length=20, default='Pendiente', choices=[
        ('Pendiente', 'Pendiente'), ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada')], verbose_name='Estado de la solicitud')
    
    class Meta:
        verbose_name = 'Solicitud de Constancia de Estudio'
        verbose_name_plural = 'Solicitudes de Constancias de Estudio'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f'Solicitud de {self.estudiante.p_nombre} - {self.estudiante.p_apellido} - {self.fecha_solicitud.strftime("%d/%m/%Y %H:%M")}'
    

