from django.apps import AppConfig


class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Menu'
    verbose_name = 'perfiles'
    
    def ready(self):
        import Menu.signals
    
