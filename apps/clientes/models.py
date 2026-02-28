from django.db import models
from django.core.exceptions import ValidationError
from apps.usuarios.models import Usuario
from django.core.exceptions import ObjectDoesNotExist


"""
Creo el modelo Cliente que tendra los siguiente campos:


freelancer: una clave foranea por que un freelancer puede tener muchos clientes pero un cliente solo puede tener un unico freelancer. 
Utilizo models.PROTECT para que el freelancer no se pueda borrar a menos que no tenga clientes asociadosya que sin freelancer los clientes no tendrían propietario y no podrían tener proyectos asociados.
Y el limit_choices_to sirve para solo poder elegir usuarios con una cuenta tipo freelancer

usuario_cliente: una clave OnetoOne por que un cliente solo puede tener un usuario y viceversa
Utilizo models.SET_NULL para que el si se borra la cuenta del usuario, en la base de datos no se pierda al cliente. Lo unico que ocurriria es que el usuario borrado no puede hacer login (evidentemente). Esto tiene sentido porque el usuario_cliente es opcional, por lo que un cliente puede existir sin un usuario asociado.
Y utilizo limits_coice_to para solo poder elegir usuarios con una cuenta tipo cliente (al contrario que el campo freelancer)


nombre = un CharField simple para escribir el nombre del cliente / compañia

email = un EmailField dedicado a almacenar el email del cliente. No deberia ser unico como en Usuario porque si no, ese cliente no se podria asignar a otro freelancer

telefono = un CharField dedicado a almacenar el telefono de un cliente. Puede ser nulo.

direccion = Un TextField dedicado a almacenar la direccion del cliente. Puede ser nulo.

estado = Un BooleanField que será True si el usuario está activo o False si el usuario no está activo



Aplico una restriccion dentro del "class Meta" para impedir que un freelancer tenga dos clientes con el mismo email.

Creo una función "clean" para asegurarnos de que se cumplen una serie de criterios antes de mandar una instancia de cliente a la base de datos
"""





class Cliente(models.Model):
    # Relaciones
    freelancer = models.ForeignKey(
        Usuario,
        # PROTECT: impide borrar el freelancer si tiene clientes asociados.
        # El freelancer no debe tener clientes para poder eliminarse.
        on_delete=models.PROTECT,
        related_name='clientes',
        related_query_name='cliente',
        verbose_name='Freelancer',
        limit_choices_to={'perfil__tipo_cuenta': 'freelancer'}
    )
    usuario_cliente = models.OneToOneField(
        Usuario,
        # SET_NULL: si el usuario cliente borra su cuenta, el registro del cliente
        # para el freelancer sigue existiendo, simplemente pierde el acceso al login.
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuenta_cliente',
        related_query_name='cuenta_cliente',
        verbose_name='Usuario cliente',
        limit_choices_to={'perfil__tipo_cuenta': 'cliente'}
    )
    # Datos del cliente
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre / Compañia'
    )
    email = models.EmailField(
        verbose_name='Email de contacto'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    estado = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        unique_together = ('freelancer', 'email')
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def clean(self):
        """
        Valida y sincroniza los datos del cliente antes de guardar.

        Validaciones:
            - El freelancer debe ser un usuario de tipo 'freelancer'.
            - El usuario cliente debe ser un usuario de tipo 'cliente'.
            - El freelancer y el usuario cliente no pueden ser el mismo usuario.
            - Ambos usuarios deben tener perfil asociado.

        Sincronización:
            - Si el cliente tiene usuario asociado, sincroniza nombre, email
            y estado con los datos del usuario para evitar duplicidad.

        Raises:
            ValidationError: Si alguna de las validaciones anteriores falla.
        """

        try:
            # Validamos que el freelancer sea de tipo freelancer
            if self.freelancer.perfil.tipo_cuenta != 'freelancer':
                raise ValidationError('El propietario debe ser un usuario de tipo freelancer')
        except ObjectDoesNotExist:
            raise ValidationError('El freelancer no tiene perfil asociado')

        # Validamos que el usuario cliente sea de tipo cliente (solo si tiene usuario asociado)
        if self.usuario_cliente:
            try:
                if self.usuario_cliente.perfil.tipo_cuenta != 'cliente':
                    raise ValidationError('El usuario cliente debe ser de tipo cliente')
            except ObjectDoesNotExist:
                raise ValidationError('El usuario cliente no tiene perfil asociado')

        # Un freelancer no puede ser su propio cliente
        if self.usuario_cliente == self.freelancer:
            raise ValidationError('El freelancer y el usuario cliente no pueden ser el mismo usuario')

        # Si tiene usuario asociado sincronizamos los datos para evitar duplicidad
        if self.usuario_cliente:
            self.email = self.usuario_cliente.email
            self.nombre = self.usuario_cliente.username
            self.estado = self.usuario_cliente.is_active

    def __str__(self) -> str:
        return f"{self.nombre} - {self.freelancer.username}"


    """
    Para forms.py

    def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.instance and self.instance.usuario_cliente:
        del self.fields['nombre']
        del self.fields['email']
        del self.fields['estado']
    """