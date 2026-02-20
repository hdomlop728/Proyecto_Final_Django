# apps/presupuestos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Presupuesto


@receiver(post_save, sender=Presupuesto)
def verificar_validez(sender, instance, **kwargs):
    """
    Señal que se ejecuta automáticamente tras cada guardado de un presupuesto.
    Si la fecha de validez ha pasado y el presupuesto no está aceptado ni rechazado,
    lo marca automáticamente como rechazado.

    Reiterando lo dicho en el models.py, esto se deberia de hacer con Celery

    Args:
        sender: El modelo que envía la señal (Presupuesto).
        instance: La instancia de Presupuesto que acaba de guardarse.
        **kwargs: Argumentos adicionales de la señal.
    """
    if instance.estado not in ('aceptado', 'rechazado') and instance.validez < timezone.now().date():
        Presupuesto.objects.filter(pk=instance.pk).update(estado='rechazado')