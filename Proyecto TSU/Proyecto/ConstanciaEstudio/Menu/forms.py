from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
