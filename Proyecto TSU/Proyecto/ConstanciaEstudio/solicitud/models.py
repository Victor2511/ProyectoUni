from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.
"""Se crea un modelo de base de datos para trabajar la informacion requerida
para generar la constancia de estudio, toda esta informacion es necesaria y se puede actualizar y migrar
a la base de datos que se utilice"""

"""Los modelos se aplican con la normalizacion de datos para mantener un orden de datos dependientes y indenpendientes
entre si llegando hasta la 3FN y separando por completo. Algunas columnas dependera de otra columna en alguna tabla. Como el id de usuario
Que se encontraria registrado originalmente en las tablas de autenticacion de DJANGO."""

# La clase DataForm permite crear un modelo de BDD para la solicitud de informacion a un estudiante.
# Estos datos navegaran hasta el admin.py que requiere esta informacion para generar la constancia de estudio.

class DataForm(models.Model):
    p_nombre = models.CharField(max_length=30, verbose_name="Primer Nombre")
    s_nombre = models.CharField(max_length=30, verbose_name="Segundo Nombre")
    p_apellido = models.CharField(max_length=30, verbose_name="Primer Apellido")
    s_apellido = models.CharField(max_length=30, verbose_name="Segundo Apellido")
    edad = models.IntegerField()
    cedula = models.IntegerField(unique=True)
    creado_en = models.DateField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pnf = models.ForeignKey('Carrera', on_delete=models.CASCADE)
    seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE)
    semestre = models.ForeignKey('Semestre', on_delete=models.CASCADE)
    turno = models.ForeignKey('Turno', on_delete=models.CASCADE)
    periodo_academico = models.ForeignKey('PeriodoAcademico', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.p_nombre} {self.s_nombre} {self.p_apellido} {self.s_apellido} - {self.cedula}'
        # Esto retorna una cadena de Strings, es decir se guardara la informacion en base a estas columnas.
    
    
# Creando la clase Carrera podemos gestionar la informacion referente a las carreras registradas y que se encuentra el estudiante.
class Carrera(models.Model):
    #Hacemos algunas constantes ya que esto no puede ser alterado y debe ser informacion unica.
    # Dentro de las constantes seran representadas como un String y su breve nombre. Esto se referenciara en las tablas y formulario.
    INFORMATICA = 'INFORMATICA' 
    CONTADURIA = 'CONTADURIA'
    ADMINISTRACION = 'ADMINISTRACION'
    COMUNICACION_SOCIAL = 'COMUNICACION SOCIAL'
    DISTRIBUCION_LOGISTICA = 'DISTRIBUCION Y LOGISTICA'
    
    #Hacer una constante CHOICES permite hacer una lista de datos para seleccionar en el formulario de solicitud.
    #Llamando en este caso a las variables constantes.
    CARRERAS_CHOICES = [
        (INFORMATICA, 'Informatica'),
        (CONTADURIA, 'Contaduria'),
        (ADMINISTRACION, 'Administracion'),
        (COMUNICACION_SOCIAL, 'Comunicacion Social'),
        (DISTRIBUCION_LOGISTICA, 'Distribucion y Logistica'),
    ]
    # Por ultimo asignamos que tipo de dato se manejara en el campo, longitud maxima, choices para llamar la constante de seleccion
    # default para dejar algun dato de esta lista por defecto.
    pnf = models.CharField(
        max_length=24,
        choices=CARRERAS_CHOICES,
        default=INFORMATICA,
        )
    
    # Funcion de cadena de texto para mantener ordenado los datos
    def __str__(self):
        return self.get_pnf_display()
    
class Seccion(models.Model): #Esta lista de secciones son solo ejemplos de que podria tener los formularios y las tablas
    SECCIONES_CHOICES = [
        (1000, 'Seccion 1000'),
        (1100, 'Seccion 1100'),
        (1200, 'Seccion 1200')
    ]
    
    n_seccion = models.IntegerField(
        choices=SECCIONES_CHOICES,
        default=1000
    )
    
    def __str__(self):
        return f'Seccion {self.n_seccion}'
    
class Semestre(models.Model):
    SEMESTRES_CHOICES = [
        (1, 'Semestre 1'),
        (2, 'Semestre 2'),
        (3, 'Semestre 3'),
        (4, 'Semestre 4'),
        (5, 'Semestre 5'),
        (6, 'Semestre 6'),
        (7, 'Semestre 7'),
        (8, 'Semestre 8'),
    ]
    
    n_semestre = models.IntegerField(
        choices=SEMESTRES_CHOICES,
        default=1
    )
    
    def __str__(self):
        return f'Semestre {self.n_semestre}'
    
class Turno(models.Model):
    MATUTINO = 'Mañana'
    VESPERTINO = 'Tarde'
    NOCTURNO = 'Noche'
    
    TURNOS_CHOICES = [
        (MATUTINO, 'Matutino'),
        (VESPERTINO, 'Vespertino'),
        (NOCTURNO, 'Nocturno'),
    ]
    
    turno = models.CharField(
        max_length=10,
        choices=TURNOS_CHOICES,
        default=MATUTINO,
    )
    
    def __str__(self):
        return f'Turno {self.turno}'
    
class PeriodoAcademico(models.Model):
    inicio = models.DateField()
    final = models.DateField()
    
    def __str__(self):
        return f'{self.inicio.strftime("%d/%m/%Y")} hasta {self.final.strftime("%d/%m/%Y")}'