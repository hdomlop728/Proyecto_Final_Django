from django.contrib import admin

from .models import Presupuesto

# Register your models here.
@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    pass