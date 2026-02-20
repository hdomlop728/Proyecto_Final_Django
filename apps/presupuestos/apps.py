from django.apps import AppConfig


class PresupuestosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #Lo he puesto porque es una buena practica y para que no salgan warnings de Django
    name = 'apps.presupuestos'

    def ready(self):
        import apps.presupuestos.signals