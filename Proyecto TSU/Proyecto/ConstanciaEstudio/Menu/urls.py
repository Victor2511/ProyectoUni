from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('inicio/', views.index, name="inicio"),
    path('registro/', views.register_student, name="register"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('recuperar-usuario/', views.recuperar_usuario, name='recuperar_usuario'),
    path('recuperar-contraseña/', views.recuperar_password, name='recuperar_password'),
]
