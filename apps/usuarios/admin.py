from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Perfil


class PerfilInline(admin.StackedInline):
    """
    Inline que muestra el Perfil asociado dentro del formulario de Usuario.

    Al tener Perfil una relación OneToOneField con Usuario, tiene sentido
    gestionarlos desde la misma pantalla del admin en lugar de navegar
    a dos secciones distintas. Así el administrador puede crear o editar
    el usuario y su perfil en una sola acción.

    can_delete = False impide borrar el perfil accidentalmente desde el
    inline del usuario. Si se quiere eliminar un perfil, debe hacerse
    desde su propia sección en el admin.
    """
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Admin para el modelo Usuario, que hereda de UserAdmin en lugar de
    ModelAdmin para conservar toda la funcionalidad que Django trae por
    defecto para la gestión de usuarios: cambio de contraseña, permisos,
    grupos, historial de acceso, etc.

    Se añade el PerfilInline para gestionar el perfil del usuario en la
    misma pantalla, y se extiende el list_display con información relevante
    como el tipo de cuenta, que en esta aplicación es clave para distinguir
    freelancers de clientes.

    search_fields incluye username y email porque son los dos campos
    por los que un administrador buscará usuarios de forma natural.
    Este search_fields también es el que usa autocomplete_fields en otros
    admins (como ProyectoAdmin) para buscar freelancers dinámicamente.
    """
    inlines = (PerfilInline,)
    list_display = (
        'username',
        'email',
        'get_tipo_cuenta',
        'is_active',
        'is_staff',
        'date_joined'
    )


    search_fields = ('username', 'email')

    @admin.display(description='Tipo de cuenta')
    def get_tipo_cuenta(self, obj):
        """
        Muestra el tipo de cuenta del perfil asociado al usuario en el listado.

        Se accede a través de la relación inversa OneToOneField (obj.perfil).
        El try/except protege el caso de que un usuario no tenga perfil creado
        todavía, devolviendo un guión en lugar de lanzar una excepción.
        """
        try:
            return obj.perfil.get_tipo_cuenta_display()
        except Perfil.DoesNotExist:
            return '-'


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Perfil.

    Aunque el perfil se puede gestionar desde el inline de Usuario, este
    admin independiente es útil para filtrar y buscar perfiles directamente,
    por ejemplo para listar todos los freelancers o buscar por NIF/CIF.

    Los fieldsets agrupan los campos en tres bloques lógicos:
        - Usuario: relación con el usuario y tipo de cuenta.
        - Datos fiscales: NIF/CIF y nombre fiscal, opcionales.
        - Preferencias: ajustes de UI del usuario (tema, idioma, formato),
          colapsados por defecto al ser campos secundarios que raramente
          necesita tocar un administrador.
    """
    list_display = (
        'perfil',
        'tipo_cuenta',
        'nif',
        'nombre_fiscal',
        'idioma',
        'tema',
        'formato_nums'
    )

    list_filter = (
        'tipo_cuenta',
        'idioma',
        'tema'
    )

    search_fields = (
        'perfil__username',
        'perfil__email',
        'nif',
        'nombre_fiscal'
    )

    fieldsets = (
        ('Usuario', {
            'fields': ('perfil', 'tipo_cuenta'),
        }),
        ('Datos fiscales', {
            'fields': ('nif', 'nombre_fiscal'),
        }),
        ('Preferencias', {
            'fields': ('tema', 'idioma', 'formato_nums'),
            'classes': ('collapse',),
        }),
    )

