from django import forms
from .models import DataForm, Carrera, Semestre, Seccion, Turno, PeriodoAcademico
"""Aqui se crea un formulario con los campos requeridos que esta vinculado al modelo de base de datos"""

class SolicitudForm(forms.ModelForm): #Se asigna distintos campos que seran llamados desde la base de datos
    class Meta:
        """Recuerda que campo deben ser tal cual los nombres registrados en el modelo de bases de datos"""
        
        model = DataForm 
        fields = ['p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'edad', 'cedula', 'pnf', 'semestre',
                'seccion', 'turno', 'periodo_academico']
        
        """Los formularios son totalmente modificables, en este caso llamando los campos registrados
        y asignandoles un nombre clave que se vera visualmente."""
        
        labels = {
            'p_nombre': 'Primer Nombre',
            's_nombre': 'Segundo Nombre',
            'p_apellido': 'Primer Apellido',
            's_apellido': 'Segundo Apellido',
            'edad': 'Edad',
            'cedula': 'Cedula',
            'pnf': 'PNF',
            'semestre': 'Semestre',
            'seccion': 'seccion',
            'turno': 'turno',
            'periodo_academico': 'Periodo academico',
        }
        
        """Con la variable widget permites la configuracion de los formularios y su entrada de datos.
        Por ejemplo: TextInput(), cuyo metodo es para recibir informacion de tipo texto."""
        
        widgets = {
            'p_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            's_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'p_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            's_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'cedula': forms.NumberInput(attrs={'class': 'form-control'}),
            'pnf': forms.Select(attrs={'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'seccion': forms.Select(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'periodo_academico': forms.Select(attrs={'class': 'form-control'}),
        }
    
    """Se puede agregar una configuracion extra para el metodo de Select(), pues con el metodo ModelChoiceField muestras
    los valores que se presentaran en el campo de seleccion registrados en el modelo de base de datos. En este caso con el modelo
    all() es para recibir todos los datos dentro del modelo."""
    
    pnf = forms.ModelChoiceField(queryset=Carrera.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    seccion = forms.ModelChoiceField(queryset=Seccion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    turno = forms.ModelChoiceField(queryset=Turno.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    periodo_academico = forms.ModelChoiceField(queryset=PeriodoAcademico.objects.all(), 
                                                widget=forms.Select(attrs={'class': 'form-control'}))