from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
import random
from werkzeug.security import generate_password_hash
from django.core.mail import send_mail

# PERFIL DE USUARIO

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')
    image = models.ImageField(default='users/usuario_defecto.jpg', upload_to='users/', verbose_name='Imagen de perfil')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Direccion')
    location = models.CharField(max_length=150, null=True, blank=True, verbose_name='Localidad')
    telephone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Telefono')
    
    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
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
        
        for _ in range(10):
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
        
        send_mail(
            'Informacion de Acceso',
            f'Hola {self.p_nombre},\n\nTu cuenta ha sido creada exitosamente. \n\nUsuario: {username}\nPassword: {password}',
            'victorgabrieljunior@gmail.com',
            [self.correo],
            fail_silently=False,
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
    
    def __str__(self):
        return f'{self.inicio.strftime("%d/%m/%Y")} hasta {self.final.strftime("%d/%m/%Y")}'
    
    
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
