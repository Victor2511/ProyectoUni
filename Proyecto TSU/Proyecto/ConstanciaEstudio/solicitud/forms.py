from django import forms
from .models import Constancia
"""Aqui se crea un formulario con los campos requeridos que esta vinculado al modelo de base de datos"""


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Constancia
        fields = ['primera_solicitud']

