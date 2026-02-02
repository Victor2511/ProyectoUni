from django.contrib import admin
from .models import Profile
from .models import student_registration, PeriodoAcademico, Documentos, CarnetEstudiantil
from django.contrib.admin import DateFieldListFilter
from .models import User
from .models import RecuperacionUsuario
from django_q.tasks import async_task
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.core.mail import EmailMessage
from Menu.tasks import generate_and_send_carnet_sync


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'location', 'telephone', 'user_group')
    search_fields = ('location', 'user__username', 'user__groups__name')
    list_filter = ('user__groups', 'location')

    def user_group(self, obj):
        return " - ".join([t.name for t in obj.user.groups.all().order_by('name')])
    
    user_group.short_description = 'Grupo'

@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('inicio', 'final')
    search_fields = ('inicio', 'final')
    list_filter = (('inicio', DateFieldListFilter), ('final', DateFieldListFilter))

class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'p_nombre', 's_nombre', 'p_apellido', 's_apellido', 
        'cedula', 'correo', 'pnf', 'seccion', 'semestre', 
        'tipo_estudiante', 'mostrar_documentos', 'creado_en'
    )
    search_fields = ('p_nombre', 'p_apellido', 'cedula', 'correo', 'pnf')
    list_filter = ('tipo_estudiante',)
    actions = ['create_user_account_action', 'generar_carnet_action']
    
    def create_user_account_action(self, request, queryset):
        for student in queryset:
            username = student.generate_username()
            if not User.objects.filter(username=username).exists():
                student.create_user_account()
                self.message_user(request, f'Usuario creado: {username}')
            else:
                self.message_user(request, f'El usuario {username} ya existe.')
    create_user_account_action.short_description = "Crear cuenta de usuario para estudiantes seleccionados"
    
    def generar_carnet_action(self, request, queryset):
        for student in queryset:
            carnet, created = CarnetEstudiantil.objects.get_or_create(
                estudiante=student,
                defaults={
                    'numero_carnet': f'CAR-{student.cedula}',
                    'emitido_en': timezone.now(),
                    'expiracion': timezone.now().date() + timezone.timedelta(days=365)
                }
            )
            if created:
                resultado = generate_and_send_carnet_sync(student.id)
                self.message_user(request, resultado)
            else:
                self.message_user(request, f'El estudiante {student.p_nombre} {student.p_apellido} ya tiene un carnet.')
    generar_carnet_action.short_description = "Generar y enviar carnet estudiantil"
    
    def mostrar_documentos(self, obj):
        url = reverse('descargar_documentos', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Ver/Descargar</a>', url)
    mostrar_documentos.short_description = "Documentos"

@admin.register(CarnetEstudiantil)
class CarnetEstudiantilAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'numero_carnet', 'emitido_en', 'expiracion', 'ver_pdf')
    search_fields = ('numero_carnet', 'estudiante__p_nombre', 'estudiante__p_apellido')
    list_filter = ('emitido_en', 'expiracion')

    def ver_pdf(self, obj):
        return format_html('<a href="{}" target="_blank">Ver PDF</a>', obj.pdf_carnet.url) if obj.pdf_carnet else "No disponible"
    ver_pdf.short_description = "Carnet en PDF"

class RecuperacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'fecha_solicitud', 'recuperado')
    list_filter = ('recuperado',)
    actions = ['recuperar_usuario']
    
    def recuperar_usuario(self, request, queryset):
        for recuperacion_request in queryset:
            if not recuperacion_request.recuperado:
                try:
                    estudiante = student_registration.objects.get(correo=recuperacion_request.correo)
                    user = User.objects.get(email=recuperacion_request.correo)
                except student_registration.DoesNotExist:
                    self.message_user(request, f'No se encontró un estudiante con el correo {recuperacion_request.correo}', level='error')
                    continue
                except User.DoesNotExist:
                    self.message_user(request, f'No se encontró un usuario con el correo {recuperacion_request.correo}', level='error')
                    continue
                
                async_task(
                    'Menu.tasks.send_email_task',
                    'Recuperación de Usuario',
                    f'Hola {estudiante.p_nombre}, \n\nTu usuario es: {user.username}\n',
                    [recuperacion_request.correo],
                )
                
                recuperacion_request.recuperado = True
                recuperacion_request.save()
                self.message_user(request, "Se han reenviado los usuarios al estudiante seleccionado")
    
    recuperar_usuario.short_description = "Recuperar Usuario"

class DocumentosAdmin(admin.ModelAdmin):
    list_display = ('mostrar_archivo', 'fecha_subida')
    search_fields = ('archivo',)
    list_filter = ('fecha_subida',)

    def mostrar_archivo(self, obj):
        return format_html('<a href="{}" target="_blank">Descargar</a>', obj.archivo.url) if obj.archivo else "No disponible"
    mostrar_archivo.short_description = "Archivo"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(student_registration, StudentRegistrationAdmin)
admin.site.register(RecuperacionUsuario, RecuperacionUsuarioAdmin)
admin.site.register(Documentos, DocumentosAdmin)
