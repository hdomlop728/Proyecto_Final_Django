from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import Proyecto
from .forms import ProyectoForm
from apps.setup.mixins import FreelancerPropietarioMixin


class ProyectoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar los proyectos del freelancer autenticado.

    Usa annotate para enriquecer cada proyecto con el número de presupuestos
    y facturas asociadas, evitando N+1 con select_related.
    Permite buscar por nombre o estado usando Q objects.
    """
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    permission_required = 'proyectos.view_proyecto'

    def get_queryset(self):
        """
        Filtra los proyectos del freelancer autenticado.
        - select_related: carga cliente en la misma consulta para evitar N+1.
        - annotate: añade num_presupuestos y num_facturas a cada proyecto
          sin hacer consultas adicionales por cada fila.
        - Q objects: permite buscar por nombre O descripción a la vez.
        """
        queryset = Proyecto.objects.filter(
            freelancer=self.request.user
        ).select_related(
            'cliente'
        ).annotate(
            # annotate: número de presupuestos por proyecto sin N+1
            num_presupuestos=Count('presupuestos', distinct=True),
            # annotate: número de facturas por proyecto sin N+1
            num_facturas=Count('presupuestos__factura', distinct=True),
        )

        busqueda = self.request.GET.get('busqueda', '')
        estado = self.request.GET.get('estado', '')

        if busqueda:
            # Q objects: busca por nombre O descripción del proyecto
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
            )

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['estados'] = Proyecto.ESTADOS
        return context


class ProyectoDetailView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DetailView):
    """
    Vista para ver el detalle de un proyecto con sus presupuestos y facturas.

    Usa select_related y prefetch_related para cargar todas las relaciones
    en el mínimo número de consultas posible, evitando N+1.
    """
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'
    permission_required = 'proyectos.view_proyecto'

    def get_queryset(self):
        """
        - select_related: carga cliente y freelancer en una sola consulta.
        - prefetch_related: carga todos los presupuestos y sus facturas
          asociadas en consultas separadas pero optimizadas, evitando N+1
          al iterar sobre presupuestos en el template.
        """
        return Proyecto.objects.select_related(
            'cliente', 'freelancer'
        ).prefetch_related(
            'presupuestos', 'presupuestos__factura'
        )


class ProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para crear un nuevo proyecto.

    Filtra el campo cliente para mostrar solo los clientes
    del freelancer autenticado.
    """
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'apps/proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.add_proyecto'

    def get_form(self, form_class=None):
        """
        Filtra los campos freelancer y cliente del formulario para mostrar
        solo los datos del freelancer autenticado.
        """
        form = super().get_form(form_class)
        form.fields['cliente'].queryset = form.fields['cliente'].queryset.filter(
            freelancer=self.request.user
        )
        return form

    def form_valid(self, form):
        """
        Asigna el freelancer autenticado antes de guardar el proyecto.
        """
        form.instance.freelancer = self.request.user
        return super().form_valid(form)


class ProyectoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, UpdateView):
    """
    Vista para editar un proyecto existente.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda editar sus proyectos.
    """
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'apps/proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.change_proyecto'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['cliente'].queryset = form.fields['cliente'].queryset.filter(
            freelancer=self.request.user
        )
        return form

    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        return super().form_valid(form)


class ProyectoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DeleteView):
    """
    Vista para eliminar un proyecto.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda eliminar sus proyectos.

    Nota: el modelo tiene on_delete=PROTECT en presupuestos, por lo que
    Django impedirá el borrado si el proyecto tiene presupuestos asociados.
    """
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.delete_proyecto'