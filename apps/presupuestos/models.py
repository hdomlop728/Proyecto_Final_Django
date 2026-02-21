from django.db import models
from django.core.exceptions import ValidationError
from apps.proyectos.models import Proyecto

"""
Creo la clase Presupuesto con los siguientes campos:
proyecto = una clave foránea, porque un proyecto puede tener muchos presupuestos, pero un presupuesto 
solo puede pertenecer a un proyecto.
Utilizo models.PROTECT para que el proyecto no se pueda borrar si tiene presupuestos asociados,
manteniendo así la trazabilidad completa: proyecto → presupuesto → factura.
Si el presupuesto ya fue convertido en factura, el PROTECT de Factura también impedirá 
borrar el presupuesto, asegurando que no se pierda información importante.


numero_serie = sera un CharField que se autocompletará con la funcion reescrita de save
fecha = un DateField para almacenar la fecha en la que se crea el presupuesto
validez = un DateField para almacenar la fecha en la que el presupuesto puede aceptarse, después de esa fecha no se
puede aceptar.
estado = un Charfield con un choice para almacenar el estado del presupuesto. Sus posibles estados son:
    - Borrador
    - Enviado
    - Aceptado
    - Rechazado
total = un DecimalField para almacenar la cantidad a abonar sin IVA
impuestos = DecimalField para almacenar una cantidad que funcionará como IVA (después de unos calculos) a multiplicar al total (por defecto: 21)
notas = un TextField opcional para almacenar cualquier comentario o aclaración adicional sobre el presupuesto.


Se añade una restriccion en "class Meta" para que en un proyecto no hayan 2 presupuestos que se llamen igual

Se reescribe save para asignar de forma automatica un nombre de serie al presupuesto

Se verifica en clean que la fecha de validez del presupuesto no sea inferior a la de creacion del presupuesto

Se crea la funcion convertir_a_factura para convertir el presupuesto a factura si cumple una serie de requisitos

La verificación de la validez se gestiona en signals.py mediante una señal post_save.

Me he puesto a informame y para que fuera completamente automatica, deberia usar 
Celery, pero la verdad creo que sobrepasa mi nivel por bastante
"""
class Presupuesto(models.Model):
    ESTADOS = (
        ('borrador', 'Borrador'),
        ('enviado', 'Enviado'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    )

    proyecto = models.ForeignKey(
        Proyecto,
        # PROTECT: impide borrar el proyecto si tiene presupuestos asociados.
        # Si el presupuesto ya fue convertido en factura, se mantiene la trazabilidad
        # completa: proyecto → presupuesto → factura.
        on_delete=models.PROTECT,
        related_name='presupuestos',
        related_query_name='presupuesto',
        verbose_name='Proyecto'
    )

    numero_serie = models.CharField(max_length=20, verbose_name='Número de serie')
    fecha = models.DateField(verbose_name='Fecha')
    validez = models.DateField(verbose_name='Fecha de validez')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador', verbose_name='Estado')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total')
    impuestos = models.DecimalField(max_digits=5, decimal_places=2, default=21, verbose_name='Impuestos (%)')
    notas = models.TextField(blank=True, null=True, verbose_name='Notas')

    class Meta:
        unique_together = ('proyecto', 'numero_serie')
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        #permisos personalizados para el grupo FREELANCER
        permissions = [
            ('puede_convertir_presupuesto', 'Puede convertir presupuesto a factura'),
        ]

    def __str__(self):
        return f"{self.proyecto.freelancer.username} - {self.id}"



    def save(self, *args, **kwargs):
        """
        Sobreescribe el metodo save para generar automáticamente el número de serie.

        El número de serie se genera con el formato 'YYYY-NNN' donde YYYY es el año
        de la fecha del presupuesto y NNN es el número correlativo de presupuestos
        de ese año. Ejemplo: 2026-001, 2026-002...

        Args:
            *args: Argumentos posicionales del metodo save original.
            **kwargs: Argumentos keyword del metodo save original.
        """
        if not self.numero_serie:
            año = self.fecha.year
            ultimo = Presupuesto.objects.filter(fecha__year=año).count() + 1
            self.numero_serie = f"{año}-{ultimo:03d}"
        super().save(*args, **kwargs)

    def clean(self):
        """
        Valida que la fecha de validez sea posterior a la fecha del presupuesto
        y que el total no sea negativo.

        Raises:
            ValidationError: Si alguna de las validaciones falla.
        """
        if self.validez and self.fecha and self.validez < self.fecha:
            raise ValidationError('La fecha de validez no puede ser anterior a la fecha del presupuesto.')

        if self.total is not None and self.total < 0:
            raise ValidationError('El total no puede ser negativo.')

    def convertir_a_factura(self):
        from django.utils import timezone
        from apps.facturas.models import Factura

        if self.estado != 'aceptado':
            raise ValidationError('Solo se pueden convertir a factura presupuestos aceptados')
        if self.validez < timezone.now().date():
            raise ValidationError('El presupuesto ha caducado, no puede convertirse en factura')

        factura = Factura.objects.create(
            presupuesto=self,
            fecha_emision=timezone.now().date(),
            fecha_vencimiento=self.validez,
            total=self.total,
            impuestos=self.impuestos,
            notas=self.notas,
        )

        # Cambiamos el estado del presupuesto a enviado una vez convertido a factura
        self.estado = 'enviado'
        self.save()

        return factura


    """
    Para el forms.py
    class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        exclude = ['numero_serie']  # se genera automáticamente en el save()
    """