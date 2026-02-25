from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Presupuesto
from .forms import PresupuestoForm
from apps.setup.mixins import FreelancerPropietarioMixin


class PresupuestoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar los presupuestos del freelancer autenticado.

    Filtra por proyecto__freelancer para mostrar solo los presupuestos
    del freelancer propietario. Permite buscar por número de serie o
    estado usando Q objects.
    """
    model = Presupuesto
    template_name = 'apps/presupuestos/presupuesto_list.html'
    context_object_name = 'presupuestos'
    permission_required = 'presupuestos.view_presupuesto'

    def get_queryset(self):
        """
        Filtra los presupuestos del freelancer autenticado.
        Usa select_related para evitar el problema N+1 al acceder
        a proyecto y cliente desde el template.
        Permite buscar por número de serie o estado usando Q objects.
        """
        queryset = Presupuesto.objects.filter(
            proyecto__freelancer=self.request.user
        ).select_related('proyecto', 'proyecto__cliente')

        busqueda = self.request.GET.get('busqueda', '')
        estado = self.request.GET.get('estado', '')

        if busqueda:
            # Q objects: busca por número de serie O por nombre de proyecto
            queryset = queryset.filter(
                Q(numero_serie__icontains=busqueda) | Q(proyecto__nombre__icontains=busqueda)
            )

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Añade los parámetros de búsqueda y los estados disponibles
        al contexto para mantenerlos en el formulario de filtrado.
        """
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['estados'] = Presupuesto.ESTADOS
        return context


class PresupuestoDetailView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DetailView):
    """
    Vista para ver el detalle de un presupuesto.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda ver sus presupuestos.
    Usa select_related para evitar el problema N+1.
    """
    model = Presupuesto
    template_name = 'apps/presupuestos/presupuesto_detail.html'
    context_object_name = 'presupuesto'
    permission_required = 'presupuestos.view_presupuesto'

    def get_queryset(self):
        """
        Usa select_related para cargar proyecto y cliente en una sola
        consulta y evitar el problema N+1 al acceder a sus datos en el template.
        """
        return Presupuesto.objects.select_related(
            'proyecto', 'proyecto__cliente', 'proyecto__freelancer'
        )


class PresupuestoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para crear un nuevo presupuesto.

    Filtra el campo proyecto para mostrar solo los proyectos
    del freelancer autenticado.
    """
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = 'apps/presupuestos/presupuesto_form.html'
    success_url = reverse_lazy('presupuesto_list')
    permission_required = 'presupuestos.add_presupuesto'

    def get_form(self, form_class=None):
        """
        Filtra el campo proyecto del formulario para mostrar
        solo los proyectos del freelancer autenticado.
        """
        form = super().get_form(form_class)
        form.fields['proyecto'].queryset = form.fields['proyecto'].queryset.filter(
            freelancer=self.request.user
        )
        return form


class PresupuestoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, UpdateView):
    """
    Vista para editar un presupuesto existente.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda editar sus presupuestos.
    Filtra el campo proyecto para mostrar solo los proyectos del freelancer.
    """
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = 'apps/presupuestos/presupuesto_form.html'
    success_url = reverse_lazy('presupuesto_list')
    permission_required = 'presupuestos.change_presupuesto'

    def get_form(self, form_class=None):
        """
        Filtra el campo proyecto del formulario para mostrar
        solo los proyectos del freelancer autenticado.
        """
        form = super().get_form(form_class)
        form.fields['proyecto'].queryset = form.fields['proyecto'].queryset.filter(
            freelancer=self.request.user
        )
        return form


class PresupuestoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DeleteView):
    """
    Vista para eliminar un presupuesto.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda eliminar sus presupuestos.
    Muestra una página de confirmación antes de borrar.

    Nota: el modelo tiene on_delete=PROTECT en Factura, por lo que
    Django impedirá el borrado si el presupuesto ya tiene factura asociada,
    manteniendo la trazabilidad proyecto → presupuesto → factura.
    """
    model = Presupuesto
    template_name = 'apps/presupuestos/presupuesto_confirm_delete.html'
    success_url = reverse_lazy('presupuesto_list')
    permission_required = 'presupuestos.delete_presupuesto'


@login_required
@permission_required('presupuestos.puede_convertir_presupuesto', raise_exception=True)
def convertir_a_factura(request, pk):
    """
    Vista FBV para convertir un presupuesto en factura.

    Solo acepta POST para evitar conversiones accidentales por GET.
    Comprueba que el presupuesto pertenece al freelancer autenticado.
    Delega la lógica de conversión al método convertir_a_factura() del modelo.

    Args:
        request: La petición HTTP.
        pk: La clave primaria del presupuesto a convertir.
    """
    presupuesto = get_object_or_404(
        Presupuesto,
        pk=pk,
        proyecto__freelancer=request.user
    )

    if request.method == 'POST':
        try:
            factura = presupuesto.convertir_a_factura()
            messages.success(request, f'Presupuesto convertido a factura {factura.numero_serie} correctamente.')
            return redirect('factura_detail', pk=factura.pk)
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('presupuesto_detail', pk=pk)

    # Si alguien intenta acceder por GET lo redirigimos al detalle
    return redirect('presupuesto_detail', pk=pk)