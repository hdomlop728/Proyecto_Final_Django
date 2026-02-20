from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Perfil

@receiver(post_save, sender=Perfil)
def asignar_grupo_perfil(sender, instance, created, **kwargs):
    """
    Señal que asigna automáticamente el grupo correspondiente al usuario
    cuando se crea su perfil según el tipo de cuenta.

    Args:
        sender: El modelo que envía la señal (Perfil).
        instance: La instancia de Perfil que acaba de guardarse.
        created: True si el perfil acaba de crearse, False si se edita.
        **kwargs: Argumentos adicionales de la señal.
    """
    if created:
        try:
            grupo = Group.objects.get(name=instance.tipo_cuenta.upper())
            instance.perfil.groups.add(grupo)
        except Group.DoesNotExist:
            pass