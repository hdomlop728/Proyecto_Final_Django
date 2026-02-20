from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Cliente

@receiver(post_save, sender=Cliente)
def asignar_grupo_cliente(sender, instance, created, **kwargs):
    """
    Señal que asigna automáticamente el grupo CLIENTE al usuario
    cuando se asocia un usuario_cliente a un cliente existente que
    antes no tenía usuario asociado.

    Args:
        sender: El modelo que envía la señal (Cliente).
        instance: La instancia de Cliente que acaba de guardarse.
        created: True si el cliente acaba de crearse, False si se edita.
        **kwargs: Argumentos adicionales de la señal.
    """
    if not created and instance.usuario_cliente:
        try:
            grupo = Group.objects.get(name='CLIENTE')
            instance.usuario_cliente.groups.add(grupo)
        except Group.DoesNotExist:
            pass