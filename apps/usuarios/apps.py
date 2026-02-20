from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #Lo he puesto porque es una buena practica y para que no salgan warnings de Django
    name = 'apps.usuarios'

    def ready(self):
        import apps.usuarios.signals