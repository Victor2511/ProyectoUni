from django.urls import path
from . import views

# Es necesario hacer una url ya que funciona como directorio
urlpatterns = [
    path('solicitud/', views.solicitar_constancia, name="solicitud")
    # Puedes agregar más patrones de URL según sea necesario
]