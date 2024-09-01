from django import forms
from django.contrib.auth.forms import UserCreationForm
from . models import RecuperacionUsuario
from django.contrib.auth.models import User
from .models import student_registration, Carrera, Semestre, Seccion, Turno, PeriodoAcademico
from django.utils.translation import gettext_lazy as _
import re
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Contraseña"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'maxlength': '128',
        }),
        help_text="Introduce una contraseña segura.",
    )
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'maxlength': '128',
        }),
        strip=False,
        help_text="Introduce la misma contraseña para verificación.",
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '150',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '30',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '30',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '254',
            }),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if re.search(r'[,\'"-]', username):
            raise ValidationError(_("El usuario no debe contener '.' ',', '\'', '\"', o '-'."))
        return username
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if re.search(r'[.,\'"-]', first_name):
            raise ValidationError(_("El nombre no debe contener '.', ',', '\'', '\"', o '-'."))
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if re.search(r'[.,\'"-]', last_name):
            raise ValidationError(_("El apellido no debe contener '.', ',', '\'', '\"', o '-'."))
        return last_name
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class RegisterForm(forms.ModelForm): #Se asigna distintos campos que seran llamados desde la base de datos
    class Meta:
        """Recuerda que campo deben ser tal cual los nombres registrados en el modelo de bases de datos"""
        
        model = student_registration 
        fields = ['p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'edad', 'cedula', 'correo', 'pnf', 'semestre',
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
            'Correo Electronico': 'Correo',
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
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
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
    
    
class RecuperacionUsuarioForm(forms.ModelForm):
    class Meta:
        model = RecuperacionUsuario
        fields = ['correo']
        labels = {
            'correo': 'Correo Electronico',
        }
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu correo'},)
        }
    
class RecuperarPasswordForm(forms.Form):
    correo = forms.EmailField(label='Correo electronico', max_length=254)