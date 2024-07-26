from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SolicitudForm

# Aqui hacemos que funcione el formulario y se envie la informacion correctamente

@login_required
def solicitud(request):
    solicitud_form = SolicitudForm()
    
    if request.method == "POST":
        solicitud_form = SolicitudForm(request.POST)
        
        if solicitud_form.is_valid():
            solicitud = solicitud_form.save(commit=False)
            solicitud.user = request.user
            solicitud.save()
            messages.success(request, 'Tu solicitud ha sido un exito')
            return redirect('inicio')
        
        
        
        
    return render(request, 'solicitud.html', {
        'title': 'Solicitud',
        'solicitud_form': solicitud_form
    })