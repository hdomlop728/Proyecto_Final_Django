from django.apps import AppConfig


class FacturasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #Lo he puesto porque es una buena practica y para que no salgan warnings de Django
    name = 'apps.facturas'

    def ready(self):
        import apps.facturas.signals
