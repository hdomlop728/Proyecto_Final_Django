from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.presupuestos.models import Presupuesto

"""
Creo el modelo Factura con los siguientes campos:

presupuesto = una clave OneToOne porque una factura solo puede generarse desde un único presupuesto
y un presupuesto solo puede convertirse en una única factura.
Utilizo models.PROTECT para que si existe una factura, no se pueda borrar el presupuesto que la originó,
manteniendo así la trazabilidad completa: proyecto → presupuesto → factura.
Esto también impide indirectamente borrar el proyecto, ya que el PROTECT de Presupuesto lo protege.

numero_serie = un CharField que se autocompletará con la función reescrita de save,
generando un número de serie único por año en formato YYYY-NNN.

fecha_emision = un DateField para almacenar la fecha en la que se emite la factura.
Se hereda de la fecha del presupuesto al convertirse.

fecha_vencimiento = un DateField para almacenar la fecha límite de pago de la factura.
Se hereda de la validez del presupuesto al convertirse.

estado = un CharField con un choice para almacenar el estado de la factura. Sus posibles estados son:
    - Pendiente
    - Parcial
    - Pagada
    - Vencida
    - Anulada

pagos = un JSONField que almacena una lista de pagos realizados sobre la factura.
Cada pago tiene la siguiente estructura:
{"fecha": "2026-01-01", "cantidad": 500.00, "metodo": "transferencia", "notas": "primer pago"}
Esta es la alternativa elegida (Opción A del enunciado) para cumplir el requisito ManyToMany
sin crear un séptimo modelo. Permite registrar varios pagos por factura y calcular estadísticas.

Se añade una restricción en "class Meta" para que no haya dos facturas con el mismo número de serie
dentro del mismo presupuesto.

Se reescribe save para asignar de forma automática un número de serie a la factura.

Se verifica en clean que la fecha de vencimiento no sea anterior a la fecha de emisión.
(No viene en el enunciado pero lo añado para mayor seguridad)

Se crea la función registrar_pago para registrar un pago en el JSONField y actualizar
automáticamente el estado de la factura según el total abonado.
(No viene en el enunciado pero lo añado para mayor control sobre los pagos)

La verificación de vencimiento se gestiona en signals.py mediante una señal post_save.


Me he puesto a informame y para que fuera completamente automatica, deberia usar 
Celery, pero la verdad creo que sobrepasa mi nivel por bastante
"""


class Factura(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('anulada', 'Anulada'),
    )

    presupuesto = models.OneToOneField(
        Presupuesto,
        on_delete=models.PROTECT,
        # PROTECT: si ya existe una factura, no se puede borrar el presupuesto
        # que la originó, para mantener la trazabilidad.
        related_name='factura',
        related_query_name='factura',
        verbose_name='Presupuesto'
    )

    numero_serie = models.CharField(max_length=20, verbose_name='Número de serie')
    fecha_emision = models.DateField(verbose_name='Fecha de emisión')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de vencimiento')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    pagos = models.JSONField(default=list, blank=True, verbose_name='Pagos')
    # Estructura de cada pago:
    # [{"fecha": "2026-01-01", "cantidad": 500.00, "metodo": "transferencia", "notas": "primer pago"}]

    class Meta:
        unique_together = ('presupuesto', 'numero_serie')
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f"{self.numero_serie} - {self.presupuesto.proyecto.cliente.nombre}"

    def save(self, *args, **kwargs):
        """
        Sobreescribe el metodo save para generar automáticamente el número de serie.

        El número de serie se genera con el formato 'YYYY-NNN' donde YYYY es el año
        de la fecha de emisión y NNN es el número correlativo de facturas de ese año.
        Ejemplo: 2026-001, 2026-002...

        Args:
            *args: Argumentos posicionales del metodo save original.
            **kwargs: Argumentos keyword del metodo save original.
        """
        if not self.numero_serie:
            año = self.fecha_emision.year
            ultimo = Factura.objects.filter(fecha_emision__year=año).count() + 1
            self.numero_serie = f"{año}-{ultimo:03d}"
        super().save(*args, **kwargs)

    def clean(self):
        """
        Valida que la fecha de vencimiento sea posterior a la fecha de emisión.

        Raises:
            ValidationError: Si la fecha de vencimiento es anterior a la fecha de emisión.
        """
        if self.fecha_vencimiento and self.fecha_emision and self.fecha_vencimiento < self.fecha_emision:
            raise ValidationError('La fecha de vencimiento no puede ser anterior a la fecha de emisión')

    def registrar_pago(self, cantidad, metodo, notas=''):
        """
        Registra un nuevo pago en el JSONField de pagos y actualiza el estado de la factura.

        Args:
            cantidad (float): Cantidad abonada en el pago.
            metodo (str): Metodo de pago utilizado. Ejemplo: transferencia, tarjeta...
            notas (str): Notas opcionales sobre el pago.

        Raises:
            ValidationError: Si la cantidad supera el total pendiente de pago.
        """
        total_pagado = sum(p['cantidad'] for p in self.pagos)
        pendiente = float(self.presupuesto.total) - total_pagado

        if cantidad > pendiente:
            raise ValidationError(f'La cantidad supera el total pendiente ({pendiente})')

        self.pagos.append({
            'fecha': timezone.now().date().isoformat(),
            'cantidad': cantidad,
            'metodo': metodo,
            'notas': notas
        })

        total_pagado += cantidad
        if total_pagado >= float(self.presupuesto.total):
            self.estado = 'pagada'
        else:
            self.estado = 'parcial'

        self.save()