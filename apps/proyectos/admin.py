from django.contrib import admin
from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'cliente',
        'freelancer',
        'fecha_inicio',
        'fecha_fin',
        'estado'
    )

    list_filter = (
        'estado',
        'freelancer'
    )

    search_fields = (
        'nombre',
    )

    list_per_page = 25

    #Es como un select pero mejor si hay muchos registros (no lo he entendido del all (Si puedo preguntar a Rivas))
    autocomplete_fields = (
        'freelancer',
        'cliente'
    )

    fieldsets = (
        ('Claves Foraneas', {
            'fields': ('freelancer', 'cliente'),
        }),
        ('Datos', {
            'fields': ('nombre', 'descripcion', 'estado'),
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin'),
        }),
    )