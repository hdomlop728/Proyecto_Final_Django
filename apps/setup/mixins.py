from django.core.exceptions import PermissionDenied

"""
IMPORTANTE:
Revisar las vistas, creo que estan bien, pero como no las estoy haciendo, 
las he puesto de cabeza.
"""


class FreelancerPropietarioMixin:
    """
    Objetivo:
        Garantizar que solo el freelancer propietario puede acceder
        a sus clientes, proyectos y documentos.

    Regla:
        Si el usuario autenticado es un freelancer y no es el propietario
        del objeto solicitado, se lanza un PermissionDenied.

    (REVISAR) Vistas donde se aplica:
        - ClienteDetailView
        - ClienteUpdateView
        - ClienteDeleteView
        - ProyectoDetailView
        - ProyectoUpdateView
        - ProyectoDeleteView
        - PresupuestoDetailView
        - PresupuestoUpdateView
        - PresupuestoDeleteView
        - FacturaDetailView
        - FacturaUpdateView
    """
    def dispatch(self, request, *args, **kwargs):
        objeto = self.get_object()
        if request.user.groups.filter(name='FREELANCER').exists():
            if objeto.freelancer != request.user:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ClientePropietarioMixin:
    """
    Objetivo:
        Garantizar que el cliente solo puede acceder a documentos
        asociados a su cuenta.

    Regla:
        Si el usuario autenticado es un cliente y el objeto solicitado
        no pertenece a su cuenta, se lanza un PermissionDenied.

    (REVISAR) Vistas donde se aplica:
        - ProyectoDetailView
        - PresupuestoDetailView
        - FacturaDetailView
    """
    def dispatch(self, request, *args, **kwargs):
        objeto = self.get_object()
        if request.user.groups.filter(name='CLIENTE').exists():
            if objeto.proyecto.cliente.usuario_cliente != request.user:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


"""
Para usar el mixin en las views:
from apps.setup.mixins import FreelancerPropietarioMixin, ClientePropietarioMixin
"""