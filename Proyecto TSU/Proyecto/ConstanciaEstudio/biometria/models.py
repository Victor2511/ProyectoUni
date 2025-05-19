from django.db import models
from Menu.models import student_registration

class FotoProcesada(models.Model):
    estudiante = models.ForeignKey(student_registration, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='fotos_procesadas/')
    fecha = models.DateTimeField(auto_now_add=True)
    