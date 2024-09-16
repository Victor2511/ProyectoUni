from django.contrib import admin
from .models import Profile
from .models import student_registration, PeriodoAcademico
from django.contrib.admin import DateFieldListFilter
from .models import User
from .models import RecuperacionUsuario
from django.core.mail import send_mail
from django_q.tasks import async_task

# PROFILE DETALLADO
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
    list_display = ('p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'cedula', 'correo', 'pnf', 'seccion', 'semestre', 'creado_en')
    search_fields = ('p_nombre', 'p_apellido', 'cedula', 'correo', 'pnf')
    
    actions = ['create_user_account_action']
    
    def create_user_account_action(self, request, queryset):
        for student in queryset:
            if not User.objects.filter(username=student.generate_username()).exists():
                user = student.create_user_account()
                self.message_user(request, f'Usuario creado: {student.generate_username()}')
                
            else:
                self.message_user(request, f'El usuario {student.generate_username()} ya existe.')
    create_user_account_action.short_description = "Crear cuenta de usuario para estudiantes seleccionados"

class RecuperacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'fecha_solicitud', 'recuperado')
    list_filter = ('recuperado',)
    actions = ['recuperar_usuario']
    
    def recuperar_usuario(self, request, queryset):
        for recuperacion_request in queryset:
            if not recuperacion_request.recuperado:
                try:
                    # Obtener el registro del estudiante usando el correo
                    estudiante = student_registration.objects.get(correo=recuperacion_request.correo)
                    user = User.objects.get(email=recuperacion_request.correo)
                except student_registration.DoesNotExist:
                    self.message_user(request, f'No se encontró un estudiante con el correo {recuperacion_request.correo}', level='error')
                    continue
                except User.DoesNotExist:
                    self.message_user(request, f'No se encontró un usuario con el correo {recuperacion_request.correo}', level='error')
                    continue
                
                # Enviar correo con usuario y contraseña
                async_task(
                    'Menu.tasks.send_email_task',
                    'Recuperacion de Usuario',
                    f'Hola {estudiante.p_nombre}, \n\nTu usuario es: {user.username}\n',
                    [recuperacion_request.correo],
                )
                
                recuperacion_request.recuperado = True
                recuperacion_request.save()
        self.message_user(request, "Se han reenviado los usuarios al estudiante seleccionado")
    
    recuperar_usuario.short_description = "Recuperar Usuario"


admin.site.register(Profile, ProfileAdmin)
admin.site.register(student_registration, StudentRegistrationAdmin)
admin.site.register(RecuperacionUsuario, RecuperacionUsuarioAdmin)

