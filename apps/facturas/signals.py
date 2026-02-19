from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Factura


@receiver(post_save, sender=Factura)
def verificar_vencimiento(sender, instance, **kwargs):
    """
    Señal que se ejecuta automáticamente tras cada guardado de una factura.
    Comprueba si la factura ha vencido y actualiza su estado en la BD.

    Reiterando lo dicho en el models.py, esto se deberia de hacer con Celery

    Args:
        sender: El modelo que envía la señal (Factura).
        instance: La instancia de Factura que acaba de guardarse.
        **kwargs: Argumentos adicionales de la señal.
    """
    if instance.estado not in ('pagada', 'anulada') and instance.fecha_vencimiento < timezone.now().date():
        Factura.objects.filter(pk=instance.pk).update(estado='vencida')