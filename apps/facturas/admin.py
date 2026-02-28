from django.contrib import admin
from .models import Factura


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):

    list_display = (
        'numero_serie',
        'presupuesto',
        'fecha_emision',
        'fecha_vencimiento',
        'total_pagado',
        'estado'
    )

    list_filter = (
        'estado',
    )

    search_fields = (
        'numero_serie',
    )


    list_per_page = 25

    readonly_fields = (
        'numero_serie',
        'total_pagado',
        'pagos'
    )

    fieldsets = (
        ('Clave Foranea', {
            'fields': ('presupuesto',),
        }),
        ('Número de serie', {
            'fields': ('numero_serie',)
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento'),
        }),
        ('Estado y pagos', {
            'fields': ('estado', 'total_pagado', 'pagos'),
        }),
    )