from django.contrib import admin
from .models import Presupuesto


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):

    list_display = (
        'numero_serie',
        'proyecto',
        'fecha',
        'validez',
        'total',
        'impuestos',
        'estado'
    )

    list_filter = ('estado',)

    search_fields = (
        'numero_serie',
        'proyecto__nombre'
    )

    list_per_page = 25

    readonly_fields = ('numero_serie',)

    fieldsets = (
        ('Clave Foranea', {
            'fields': ('proyecto', ),
        }),
        ('Número de serie', {
            'fields': ('numero_serie',),
        }),
        ('Fechas', {
            'fields': ('fecha', 'validez'),
        }),
        ('Importes y estado', {
            'fields': ('total', 'impuestos', 'estado'),
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
    )