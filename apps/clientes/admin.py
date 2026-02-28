from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'email',
        'telefono',
        'freelancer',
        'usuario_cliente',
        'estado',
    )

    list_filter = ('estado', 'freelancer')

    search_fields = (
        'nombre',
        'email',
    )

    list_per_page = 25

    fieldsets = (
        ('Claves Foraneas', {
            'fields': ('freelancer', 'usuario_cliente'),
        }),
        ('Datos del cliente', {
            'fields': ('nombre', 'email', 'telefono', 'direccion'),
        }),
        ('Estado', {
            'fields': ('estado',),
        }),
    )