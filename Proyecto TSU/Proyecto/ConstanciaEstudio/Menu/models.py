import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.forms import ValidationError
from django.utils import timezone
from django.conf import settings
import random
from werkzeug.security import generate_password_hash
from django_q.tasks import async_task
from django.core.validators import FileExtensionValidator
from django.utils.html import format_html
from datetime import timedelta

# PERFIL DE USUARIO

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')
    image = models.ImageField(default='users/usuario_defecto.jpg', upload_to='users/', verbose_name='Imagen de perfil')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Direccion')
    location = models.CharField(max_length=150, null=True, blank=True, verbose_name='Localidad')
    telephone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Telefono')
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-id']
    
    def __str__(self):
        return self.user.username
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

class student_registration(models.Model):
    p_nombre = models.CharField(max_length=30, verbose_name="Primer Nombre")
    s_nombre = models.CharField(max_length=30, verbose_name="Segundo Nombre")
    p_apellido = models.CharField(max_length=30, verbose_name="Primer Apellido")
    s_apellido = models.CharField(max_length=30, verbose_name="Segundo Apellido")
    edad = models.IntegerField()
    cedula = models.IntegerField(unique=True)
    correo = models.EmailField(verbose_name='Correo Electronico', unique=True)
    creado_en = models.DateField(default=timezone.now)
    pnf = models.ForeignKey('Carrera', on_delete=models.CASCADE)
    seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE)
    semestre = models.ForeignKey('Semestre', on_delete=models.CASCADE)
    turno = models.ForeignKey('Turno', on_delete=models.CASCADE)
    periodo_academico = models.ForeignKey('PeriodoAcademico', on_delete=models.CASCADE)
    tipo_estudiante = models.ForeignKey('TipoEstudiante', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Estudiante Registrado'
        verbose_name_plural = 'Estudiantes Registrados'
    
    def __str__(self):
        return f'{self.p_nombre} {self.s_nombre} {self.p_apellido} {self.s_apellido} - {self.cedula} - {self.correo}'
        # Esto retorna una cadena de Strings, es decir se guardara la informacion en base a estas columnas.
    
    def generate_username(self):
        # Generar el usuario con la inicial del primer nombre, apellido y cedula
        return f'{self.p_nombre[0].lower()}{self.p_apellido[0].lower()}{self.cedula}'
    
    def generate_password(self):
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
    
    def create_user_account(self):
        # Crear el usuario en el sistema de autenticacion
        username = self.generate_username()
        password = self.generate_password()
        
        user = User.objects.create_user(
            username=username, 
            email=self.correo, 
            password=password,
            first_name=self.p_nombre,
            last_name=self.p_apellido
            )
        user.save()
        
        # Enviar correo usando Django-Q
        async_task(
            'Menu.tasks.send_email_task',  # Nombre completo del módulo y función
            'Información de Acceso',
            f'Hola {self.p_nombre},\n\nTu cuenta ha sido creada exitosamente. \n\nUsuario: {username}\nContraseña: {password}',
            [self.correo]
        )
        
    def set_new_password(self, new_password):
        user = User.objects.get(email=self.correo)
        user.set_password(new_password)
        user.save()
    
    
    
        return user
    
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
    
    class Meta:
        verbose_name = 'Periodo Academico'
        verbose_name_plural = 'Periodos Academicos'
    
    def __str__(self):
        return f'{self.inicio.strftime("%d/%m/%Y")} hasta {self.final.strftime("%d/%m/%Y")}'
    
    
class TipoEstudiante(models.Model):
    REGULAR = 'Regular'
    NUEVO_INGRESO = 'Nuevo Ingreso'
    
    TIPO_CHOICES = [
        (REGULAR, 'Regular'),
        (NUEVO_INGRESO, 'Nuevo Ingreso')
    ]
    
    tipo_estudiante = models.CharField(
        max_length=15,
        default=REGULAR,
        null=False,
        blank=False,
        choices=TIPO_CHOICES,
    )
    def __str__(self):
        return self.tipo_estudiante

class Documentos(models.Model):
    FOTO_CARNET = 'Foto Carnet'
    CEDULA = 'Cédula'
    NOTAS = 'Notas Certificadas'
    TITULO = 'Título'
    PARTIDA_NACIMIENTO = 'Partida de Nacimiento'
    
    TIPO_DOCUMENTO_CHOICES = [
        (FOTO_CARNET, 'Foto Carnet'),
        (CEDULA, 'Cédula'),
        (NOTAS, 'Notas Certificadas'),
        (TITULO, 'Título'),
        (PARTIDA_NACIMIENTO, 'Partida de Nacimiento'),
    ]

    estudiante = models.ForeignKey(
        student_registration,
        on_delete=models.CASCADE,
        related_name="documentos"
    )
    tipo_documento = models.CharField(
        max_length=25,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento"
    )
    archivo = models.FileField(
        upload_to='documentos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])],
        verbose_name="Archivo"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return f"{self.tipo_documento} - {self.estudiante.p_nombre} {self.estudiante.p_apellido}"


class CarnetEstudiantil(models.Model):
    estudiante = models.OneToOneField(
        'student_registration',  # Ajustamos el nombre del modelo
        on_delete=models.CASCADE,
        verbose_name='Estudiante'
    )
    numero_carnet = models.CharField(max_length=20, unique=True, verbose_name='Número de Carnet')
    codigo_barras = models.ImageField(upload_to='carnets/', verbose_name='Código de Barras')
    emitido_en = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Emisión')
    expiracion = models.DateField(
        verbose_name='Fecha de Expiración',
        default=timezone.now() + timedelta(days=365)  # Expira en 1 año por defecto
    )
    pdf_carnet = models.FileField(upload_to='carnets_pdf/', null=True, blank=True, verbose_name='Carnet en PDF')

    class Meta:
        verbose_name = 'Carnet Estudiantil'
        verbose_name_plural = 'Carnets Estudiantiles'

    def __str__(self):
        return f'Carnet - {self.estudiante.p_nombre} {self.estudiante.p_apellido}'

class RecuperacionUsuario(models.Model):
    #correo = models.ForeignKey('student_registration', on_delete=models.CASCADE, null=True, blank=True)
    correo = models.EmailField(verbose_name='Correo Electronico', null=True, blank=True)
    fecha_solicitud = models.DateTimeField(default=timezone.now, verbose_name='Fecha de solicitud')
    recuperado = models.BooleanField(default=False, verbose_name='Recuperado')
    
    class Meta:
        verbose_name = 'Solicitud de Recuperacion'
        verbose_name_plural = 'Solicitudes de Recuperacion'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f'Solicitud de recuperacion de {self.correo} el {self.fecha_solicitud.strftime("%d/%m/%Y")}'
