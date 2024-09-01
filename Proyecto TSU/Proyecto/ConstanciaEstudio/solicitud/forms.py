from django import forms
from .models import Constancia
"""Aqui se crea un formulario con los campos requeridos que esta vinculado al modelo de base de datos"""

""" Actualizacion: Para validar de forma booleano el formulario y que sea tipo checkbox usaremos el campo primera_solicitud """

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Constancia
        fields = ['primera_solicitud']

