from django.core.exceptions import ValidationError
from django.db import models
from apps.usuarios.models import Usuario
from apps.clientes.models import Cliente

"""
El modelo Proyecto cuenta con los siguientes campos:

freelancer = una clave foranea, por que un freelancer puede tener muchos proyectos pero un proyecto solo puede tener un unico freelancer. 
Utilizo models.PROTECT para que el freelancer no se pueda borrar a menos que no tenga proyectos asociados (no viene en el enunciado pero, lo he hecho para mayor seguridad) y, de esta manera, el proyecto no se quede "cojo" de freelancer.
Y el limit_choices_to sirve para solo poder elegir usuarios con una cuenta tipo freelancer

cliente = una clave foranea, por que un cliente puede tener muchos proyectos pero un proyecto solo puede tener un unico cliente.
Utilizo models.PROTECT para que el cliente no se pueda borrar a menos que no tenga proyectos asociados y, de esta manera, el proyecto no queda sin el cliente que lo inicio, en primera instancia.
No necesita un limit_choices_to porque un cliente siempre será un cliente


nombre = un CharField para almacenar el nombre del proyecto.
descripcion = un TextField para almacenar la descripcion del proyecto.
estado = un CharField para almacenar el estado del proyecto. Los posibles estados son 3:
    - Activo
    - Pausado
    - Finalizado
fecha_inicio = un DateTimeField para almacenar la fecha de inicio del proyecto
fecha_fin = un DateTimeField para almacenar la fecha de inicio del proyecto


Aplico una restriccion dentro del "class Meta" para impedir que un cliente tenga dos proyectos con el mismo nombre.

Y la función clean verifica si la fecha de inicio y fin existen (esta ultima sobre todo) y, si es así, comprueba que la fecha de inicio no sea posterior a la de fin.
"""



# Create your models here.
class Proyecto(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado')
    )

    freelancer = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='proyectos',
        related_query_name='proyecto',
        verbose_name='Freelancer',
        limit_choices_to={'perfil__tipo_cuenta': 'freelancer'}
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='proyectos',
        related_query_name='proyecto',
        verbose_name='Cliente',
    )


    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    estado = models.CharField(max_length=20, choices=ESTADOS, verbose_name='Estado')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(null=True, blank=True, verbose_name='Fecha de fin')



    class Meta:
        unique_together = ('nombre', 'cliente')
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.nombre

    def clean(self):
        """
        Valida que la fecha de fin sea posterior a la fecha de inicio.

        Raises:
            ValidationError: Si la fecha de fin es anterior a la fecha de inicio.
        """
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio')
