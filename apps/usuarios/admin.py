from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    pass


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    pass