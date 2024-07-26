from django.db import models

# Create your models here.
class Admin():
    user = models.CharField(max_length=50, verbose_name="Usuario")
    password = models.CharField(max_length=50, verbose_name="Contraseña")