from django.shortcuts import render, redirect
from django.contrib import messages
from Menu.forms import RegisterForm
from .models import student_registration
from .forms import RecuperacionUsuarioForm
from .models import RecuperacionUsuario
from .forms import RecuperarPasswordForm
import random
from werkzeug.security import generate_password_hash
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

# Creacion del menu principal

def index(request):
    
    return render(request, 'mainapp/index.html', {
        'title': 'Inicio'
    })
    
def about(request):
    
    return render(request, 'mainapp/about.html', {
        'title': 'Sobre nosotros'
    })
    

# Funcion para validar el registro del estudiante
def register_student(request):
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Te has registrado correctamente.')
            return redirect('inicio')
        else:
            messages.error(request, 'Hubo un error en el formulario.')
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {
        'title': 'Registro de Estudiante',
        'form': form,
    })



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
        
# Funcion para validar la recuperacion del usuario.
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
    
#Reciclaje del generador de password.
def generate_password():
        minus = "abcdefghijklmnopqrstuvwxyz"
        mayus = minus.upper()
        numeros = "0123456789"
        simbolos = "@()[]{}*,;/-_¿?¡!$<#>&+%="
        
        base = minus + mayus + numeros + simbolos
        longitud = 12
        
        for _ in range(10):
            muestra = random.sample(base, longitud)
            password = "".join(muestra)
            password_encriptado = generate_password_hash(password)
            print("{} => {}".format(password, password_encriptado)) #Esto se puede quitar.
        
        return password
    
# Funcion para validar la recuperacion de password y asignar una nueva.
def recuperar_password(request):
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo'] # Validar el campo correo
            try:
                estudiante = student_registration.objects.get(correo=correo) # Referencia del correo para buscar al estudiante.
            except student_registration.DoesNotExist:
                try:
                    estudiante = student_registration.objects.get(correo=correo)
                except student_registration.DoesNotExist:
                    messages.error(request, 'No se encontró un usuario con ese correo electrónico o nombre de usuario.')
                    return redirect('recuperar_contraseña')
            
            nueva_password = generate_password()
            estudiante.set_new_password(nueva_password) # Asignamos la nueva password generada.

            send_mail(
                'Recuperación de Contraseña',
                f'Hola {estudiante.p_nombre},\n\nTu contraseña ha sido restablecida. Tu nueva contraseña es: {nueva_password}',
                #'(Recuerda poner tu correo)',
                [estudiante.correo],
                fail_silently=False,
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
