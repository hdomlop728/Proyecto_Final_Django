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
        # Evitar llamar a get_object si la view no lo implementa o falla.
        if not hasattr(self, 'get_object') or not callable(getattr(self, 'get_object')):
            return super().dispatch(request, *args, **kwargs)
        try:
            objeto = self.get_object()
        except Exception:
            return super().dispatch(request, *args, **kwargs)

        if request.user.groups.filter(name='FREELANCER').exists():
            owner = None
            # distintos modelos exponen la relación con el freelancer de formas
            # diferentes: algunos tienen 'freelancer' directo, otros via proyecto
            try:
                if hasattr(objeto, 'freelancer'):
                    owner = objeto.freelancer
                elif hasattr(objeto, 'proyecto') and hasattr(objeto.proyecto, 'freelancer'):
                    owner = objeto.proyecto.freelancer
                elif hasattr(objeto, 'presupuesto') and hasattr(objeto.presupuesto, 'proyecto'):
                    owner = objeto.presupuesto.proyecto.freelancer
            except Exception:
                owner = None
            if owner and owner != request.user:
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
        # Evitar llamar a get_object si la view no lo implementa o falla.
        if not hasattr(self, 'get_object') or not callable(getattr(self, 'get_object')):
            return super().dispatch(request, *args, **kwargs)
        try:
            objeto = self.get_object()
        except Exception:
            return super().dispatch(request, *args, **kwargs)

        if request.user.groups.filter(name='CLIENTE').exists():
            owner_user = None
            try:
                # si el objeto tiene 'cliente' directo
                if hasattr(objeto, 'cliente') and hasattr(objeto.cliente, 'usuario_cliente'):
                    owner_user = objeto.cliente.usuario_cliente
                # si el objeto tiene 'proyecto' (ej. presupuesto, factura indirecta)
                elif hasattr(objeto, 'proyecto') and hasattr(objeto.proyecto, 'cliente'):
                    owner_user = objeto.proyecto.cliente.usuario_cliente
                # si el objeto tiene 'presupuesto' -> proyecto -> cliente
                elif hasattr(objeto, 'presupuesto') and hasattr(objeto.presupuesto, 'proyecto'):
                    owner_user = objeto.presupuesto.proyecto.cliente.usuario_cliente
            except Exception:
                owner_user = None
            if owner_user and owner_user != request.user:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


"""
Para usar el mixin en las views:
from apps.setup.mixins import FreelancerPropietarioMixin, ClientePropietarioMixin
"""