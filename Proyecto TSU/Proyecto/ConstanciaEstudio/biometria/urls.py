from django.urls import path
from . import views

urlpatterns = [
    #path('captura/', views.captura, name='captura'),
    path('guardar_foto/', views.guardar_foto_carnet_procesada, name='procesar_foto'),
]
