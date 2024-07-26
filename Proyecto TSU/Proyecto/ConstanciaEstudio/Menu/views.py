from django.shortcuts import render, redirect
from django.contrib import messages
from Menu.forms import CustomUserCreationForm
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
    
# Funcion para la pagina de registro de usuarios
def register_page(request):
    #Condicion si el usuario se identifica redirije a la pagina de inicio
    if request.user.is_authenticated:
        return redirect('inicio')
    else:
        # Esta funcion llama al formulario de registro en forms.py
        register_form = CustomUserCreationForm()
        # Validacion y guardado de usuario a la base de datos
        if request.method == 'POST':
            register_form = CustomUserCreationForm(request.POST)
            
            if register_form.is_valid():
                register_form.save()
                messages.success(request, 'Te has registrado correctamente')
                
                return redirect('inicio')
            
        return render(request, 'users/register.html', {
            'title': 'Registro',
            'register_form': register_form
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
# Funcion de cerrar sesion
def logout_user(request):
    logout(request)
    return redirect('login')