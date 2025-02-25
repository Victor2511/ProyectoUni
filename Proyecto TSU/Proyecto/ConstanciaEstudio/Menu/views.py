from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from Menu.forms import RegisterForm, DocumentForm
from .models import student_registration, Documentos
from .forms import RecuperacionUsuarioForm
from .forms import RecuperarPasswordForm
import random
from werkzeug.security import generate_password_hash
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django_q.tasks import async_task
import os
import zipfile
import io
from django.http import HttpResponse
from django.conf import settings


def index(request):
    
    return render(request, 'main/main.html', {
        'title': 'Inicio'
    })


# Crear el formset para los documentos con los campos correctos
DocumentosFormSet = inlineformset_factory(
    student_registration,
    Documentos,
    form=DocumentForm,
    fields=('tipo_documento', 'archivo',),
    extra=4,  # Permite hasta 4 documentos adicionales
    can_delete=False
)

def register_student(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            student = form.save()  # Guardar primero el estudiante

            # Crear el formset con la instancia del estudiante
            document_formset = DocumentosFormSet(request.POST, request.FILES, instance=student)

            if document_formset.is_valid():
                document_formset.save()  # Guardar los documentos
                messages.success(request, 'Te has registrado correctamente.')
                return redirect('inicio')
            else:
                messages.error(request, 'Hubo un error al procesar los documentos.')
        else:
            messages.error(request, 'Hubo un error en el formulario.')
    else:
        form = RegisterForm()
        document_formset = DocumentosFormSet()

    return render(request, 'users/register.html', {
        'title': 'Registro de Estudiante',
        'form': form,
        'document_formset': document_formset,
    })

def descargar_documentos(request, student_id):
    student = get_object_or_404(student_registration, pk=student_id)
    documentos = Documentos.objects.filter(estudiante=student)

    if not documentos.exists():
        messages.error(request, "Este estudiante no tiene documentos para descargar.")
        return redirect('alguna_vista')

    zip_filename = f"documentos_estudiante_{student_id}.zip"

    # Crear ZIP en memoria en lugar de escribirlo en disco
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for documento in documentos:
            file_path = documento.archivo.path
            zip_file.write(file_path, os.path.basename(file_path))

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    return response


#Funcion del login
def login_page(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    #Aqui se obtiene informacion de la base de datos y obtiene los datos correspondientes
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            # Esta condicion permite que el usuario rellene el formulario correctamente
            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                messages.warning(request, 'No te has identificado correctamente')
            
            
        return render(request, 'users/login.html', {
            'title': 'Identificate'
        })
        

def recuperar_usuario(request):
    recuperar_usuario = RecuperacionUsuarioForm()
    
    if request.method == "POST":
        recuperar_usuario = RecuperacionUsuarioForm(request.POST)
        
        if recuperar_usuario.is_valid():
            recuperacion = recuperar_usuario.save(commit=False)
            
            try:
                estudiante = student_registration.objects.get(correo=recuperacion.correo)
            except student_registration.DoesNotExist:
                messages.error(request, 'No se encontró el registro del estudiante en la base de datos.')
                return redirect('recuperar_usuario')
            
            recuperacion.save()
            messages.success(request, 'Tu solicitud ha sido un éxito.')
            return redirect('inicio')
    
    return render(request, 'users/recuperar_usuario.html', {
        'title': 'Recuperación de Usuario',
        'form': recuperar_usuario,
    })
    
    
def generate_password():
        minus = "abcdefghijklmnopqrstuvwxyz"
        mayus = minus.upper()
        numeros = "0123456789"
        simbolos = "@()[]{}*,;/-_¿?¡!$<#>&+%="
        
        base = minus + mayus + numeros + simbolos
        longitud = 12
        
        for _ in range(1):
            muestra = random.sample(base, longitud)
            password = "".join(muestra)
            password_encriptado = generate_password_hash(password)
            print("{} => {}".format(password, password_encriptado))
        
        return password
    

def recuperar_password(request):
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                estudiante = student_registration.objects.get(correo=correo)
            except student_registration.DoesNotExist:
                try:
                    estudiante = student_registration.objects.get(correo=correo)
                except student_registration.DoesNotExist:
                    messages.error(request, 'No se encontró un usuario con ese correo electrónico o nombre de usuario.')
                    return redirect('recuperar_contraseña')
            
            nueva_password = generate_password()
            estudiante.set_new_password(nueva_password)
            
            async_task(
                'Menu.tasks.send_email_task',
                'Recuperación de Contraseña',
                f'Hola {estudiante.p_nombre},\n\nTu contraseña ha sido restablecida. Tu nueva contraseña es: {nueva_password}',
                [estudiante.correo],
            )

            messages.success(request, 'Se ha enviado una nueva contraseña a tu correo electrónico.')
            return redirect('inicio')
    else:
        form = RecuperarPasswordForm()

    return render(request, 'users/recuperar_password.html', {
        'title': 'Recuperar Contraseña',
        'form': form,
    })
    
    
# Funcion de cerrar sesion
@login_required
def logout_user(request):
    logout(request)
    return redirect('login')
