from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SolicitudForm
from Menu.models import student_registration

# Aqui hacemos que funcione el formulario y se envie la informacion correctamente

@login_required
def solicitar_constancia(request):
    solicitud_form = SolicitudForm()
    
    if request.method == "POST":
        solicitud_form = SolicitudForm(request.POST)
        
        if solicitud_form.is_valid():
            solicitud = solicitud_form.save(commit=False)
            
            try:
                estudiante = student_registration.objects.get(correo=request.user.email)
            except student_registration.DoesNotExist:
                messages.error(request, 'No se encontro el registro del estudiante en la base de datos.')
                return redirect('inicio')
            
            solicitud.estudiante = estudiante
            solicitud.save()
            messages.success(request, 'Tu solicitud ha sido un exito')
            return redirect('inicio')
        
        
        
    return render(request, 'solicitud.html', {
        'title': 'Solicitud',
        'solicitud_form': solicitud_form
    })
    