from django import forms
from django.contrib.auth.forms import UserCreationForm
from . models import RecuperacionUsuario
from django.contrib.auth.models import User
from .models import student_registration, Carrera, Semestre, Seccion, Turno, PeriodoAcademico, Documentos, CarnetEstudiantil, TipoEstudiante
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


class RegisterForm(forms.ModelForm):
    # Campos relacionados con modelos de selección
    pnf = forms.ModelChoiceField(queryset=Carrera.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    seccion = forms.ModelChoiceField(queryset=Seccion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    turno = forms.ModelChoiceField(queryset=Turno.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    periodo_academico = forms.ModelChoiceField(queryset=PeriodoAcademico.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    tipo_estudiante = forms.ModelChoiceField(queryset=TipoEstudiante.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = student_registration
        fields = [
            'p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'edad', 'cedula', 'correo',
            'pnf', 'semestre', 'seccion', 'turno', 'periodo_academico', 'tipo_estudiante',
        ]

        labels = {
            'p_nombre': 'Primer Nombre',
            's_nombre': 'Segundo Nombre',
            'p_apellido': 'Primer Apellido',
            's_apellido': 'Segundo Apellido',
            'edad': 'Edad',
            'cedula': 'Cédula',
            'correo': 'Correo Electrónico',
            'pnf': 'PNF',
            'semestre': 'Semestre',
            'seccion': 'Sección',
            'turno': 'Turno',
            'periodo_academico': 'Periodo Académico',
            'tipo_estudiante': 'Tipo de Estudiante',
        }

        widgets = {
            'p_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Nombre'}),
            's_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Nombre'}),
            'p_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'}),
            's_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad'}),
            'cedula': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cédula'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
        }


# Formulario para documentos adicionales
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Documentos
        fields = ('tipo_documento', 'archivo',)
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño del archivo (5MB)
            max_tamano_mb = 5
            if archivo.size > max_tamano_mb * 1024 * 1024:
                raise forms.ValidationError(f"El archivo no puede superar los {max_tamano_mb} MB.")

            # Validar tipo de archivo permitido
            extensiones_permitidas = ['pdf', 'jpg', 'png']
            if not archivo.name.lower().endswith(tuple(extensiones_permitidas)):
                raise forms.ValidationError("Solo se permiten archivos en formato PDF, JPG o PNG.")
        return archivo

# Crear un inline formset para asociar documentos al registro de estudiante
DocumentFormSet = forms.inlineformset_factory(
    student_registration,
    Documentos,
    form=DocumentForm,
    extra=1,
    can_delete=True
)


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
    correo = forms.EmailField(
        label='Correo electronico', 
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Introduce tu correo'
            }
        )
    )