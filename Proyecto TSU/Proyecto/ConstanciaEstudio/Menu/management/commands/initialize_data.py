from typing import Any
from django.core.management.base import BaseCommand
from Menu.models import Carrera, Turno, Semestre, Seccion, PeriodoAcademico
from datetime import date

"""Lo que esta a continuacion es un Script de automatizacion de creacion de datos. Ayuda para ingresar datos de ejemplo o
agregar nuevos datos que se guardaran en las tablas correspondientes. En este caso esta funcion me permite registrar las carreras,
turnos, secciones, semestres disponibles. Esto es totalmente modificable y se puede agregar o eliminar cualquier dato de ser neceseario.

Recuerda hacer un makemigrations y migrate de Django desde la terminal, pues esta funcion trabaja con el modelo completamente
y se debe aplicar cambios."""

class Command(BaseCommand):
    help = 'Crea datos iniciales para la base de datos'
    
    
    def handle(self, *args, **kwargs):
        Carrera.objects.get_or_create(pnf='Informatica')
        Carrera.objects.get_or_create(pnf='Contaduria')
        Carrera.objects.get_or_create(pnf='Administracion')
        Carrera.objects.get_or_create(pnf='Comunicacion Social')
        Carrera.objects.get_or_create(pnf='Distribucion y Logistica')
        
        Turno.objects.get_or_create(turno='Matutino')
        Turno.objects.get_or_create(turno='Vespertino')
        Turno.objects.get_or_create(turno='Nocturno')
        
        Seccion.objects.get_or_create(n_seccion=1000)
        Seccion.objects.get_or_create(n_seccion=1100)
        Seccion.objects.get_or_create(n_seccion=1200)
        
        for semestre in range(1,9):
            Semestre.objects.get_or_create(n_semestre=semestre)
        
        inicio = date(2024, 1, 1)
        final = date(2025, 12, 31)
        
        PeriodoAcademico.objects.get_or_create(inicio=inicio, final=final)
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales creados correctamente'))