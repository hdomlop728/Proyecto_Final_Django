from django.db import models
from django.contrib.auth.models import AbstractUser
import re


"""
Para empezar crearé el modelo Usuario heredando de AbstractUser.

AbstractUser es una clase de Django que ya trae campos por defecto como:

username: que será nuestro "nombre_visible"
email: modificaremos para añadirle la restriccion: unique=True
is_active: sera nuestro "estado"

Por lo que solo modificaré el campo email para añadirle la restricción
"""

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self) -> str:
        return f"{self.username} - {self.email}"

"""
Para Django reconozca este modelo como el por defecto en setting.py deberemos cambiar la siguiente línea:

AUTH_USER_MODEL = 'usuarios.Usuario' (nombre_app.NombreModelo)
"""



"""
Con el modelo Usuario creado, creo el modelo Perfil que tendrá los siguientes campos:

perfil: que será una relación 1 a 1 con Usuario. 
Tiene un models.CASCADE, para que cuando se borre un perfil usuario lo haga tambien el perfil,
porque si el usuario del perfil no existe, no tiene ningun sentido seguir almacenandolo


tipo_cuenta = será un CharField con un choice para elegir entre "freelancer" o "cliente"
nif = será un campo CharField opcional en el que se podrá dejar en blanco y se encargará de almacenar el NIF
nombre_fiscal = será exactamente igual que el "nif" pero con el nombre fiscal
tema = será un CharField con un choice para elegir entre "oscuro" o "claro"
idiomas = será un CharField con un choice para elegir entre "es" o "en"
formato_nums = será un CharField con un choice para elegir entre "es" o "en". Tambien tendrá una funcion de validacion para modificar la visualizacion de los valores según se escoja una u opción
"""


class Perfil(models.Model):
    TIPO_CUENTA = (
        ("freelancer", "Freelancer"),
        ("cliente", "Cliente")
    )

    TEMAS = (
        ('claro', 'Claro'),
        ('oscuro', 'Oscuro')
    )

    IDIOMAS = (
        ('es', 'Español'),
        ('en', 'Inglés')
    )

    FORMATOS_NUMS = (
        ('es', 'Español (1.000,00)'),
        ('en', 'Inglés (1,000.00)'),
    )

    perfil = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )

    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TIPO_CUENTA,
        default="freelancer",
        verbose_name='Tipo de cuenta'
    )


    #Datos Fiscales
    nif = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='NIF/CIF'
    )

    nombre_fiscal = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre fiscal'
    )


    #Preferencias
    tema = models.CharField(
        max_length=10,
        choices=TEMAS,
        default='claro',
        verbose_name = 'Tema'
    )

    idioma = models.CharField(
        max_length=5,
        choices=IDIOMAS,
        default='es',
        verbose_name = 'Idioma'
    )

    formato_nums = models.CharField(
        max_length=5,
        choices=FORMATOS_NUMS,
        default='es',
        verbose_name='Formato de números'
    )


    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'


    def __str__(self) -> str:
        return f"{self.perfil.username} - {self.tipo_cuenta}"

    def clean(self):
        """
        Valida el formato del NIF (persona física) o CIF (empresa).
        NIF: 8 números + 1 letra. Ej: 12345678A
        CIF: 1 letra + 7 números + 1 letra o número. Ej: B12345678
        Solo valida si el campo está relleno, ya que es opcional.

        Raises:
            ValidationError: Si el formato del NIF o CIF no es válido.
        """
        from django.core.exceptions import ValidationError
        if self.nif:
            nif_pattern = r'^\d{8}[A-Z]$'
            cif_pattern = r'^[A-Z]\d{7}[A-Z0-9]$'
            if not re.match(nif_pattern, self.nif) and not re.match(cif_pattern, self.nif):
                raise ValidationError('El formato del NIF/CIF no es válido. NIF: 12345678A | CIF: B12345678')

    def formatear_numero(self, valor):
        """
        Formatea un número según las preferencias de idioma del perfil.

        Args:
            valor (float): Valor numérico a formatear.

        Returns:
            str: Número formateado según el formato del perfil.
                 Español: 1.000,00 | Inglés: 1,000.00
        """
        if self.formato_nums == 'es':
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return f"{valor:,.2f}"