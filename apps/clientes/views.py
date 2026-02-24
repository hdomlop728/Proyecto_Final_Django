from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm
from apps.setup.mixins import FreelancerPropietarioMixin


class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar los clientes del freelancer autenticado.

    Solo muestra los clientes del freelancer propietario.
    Permite buscar por nombre, email o estado mediante Q objects.
    """
    model = Cliente
    template_name = 'apps/clientes/cliente_list.html'
    context_object_name = 'clientes'
    permission_required = 'clientes.view_cliente'

    def get_queryset(self):
        """
        Filtra los clientes del freelancer autenticado.
        Permite buscar por nombre o email y filtrar por estado
        usando Q objects para combinar condiciones.
        """
        queryset = Cliente.objects.filter(freelancer=self.request.user)

        busqueda = self.request.GET.get('busqueda', '')
        estado = self.request.GET.get('estado', '')

        if busqueda:
            # Q objects: busca por nombre O email y además filtra por freelancer
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | Q(email__icontains=busqueda)
            )

        if estado == 'activo':
            queryset = queryset.filter(estado=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(estado=False)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Añade los parámetros de búsqueda al contexto para mantenerlos
        en el formulario de búsqueda tras el filtrado.
        """
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['estado'] = self.request.GET.get('estado', '')
        return context


class ClienteDetailView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DetailView):
    """
    Vista para ver el detalle de un cliente.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda acceder al detalle de sus clientes.
    """
    model = Cliente
    template_name = 'apps/clientes/cliente_detail.html'
    context_object_name = 'cliente'
    permission_required = 'clientes.view_cliente'


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para crear un nuevo cliente.

    Asigna automáticamente el freelancer autenticado como propietario
    y pasa el freelancer al formulario para validar duplicados de email.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'apps/clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    permission_required = 'clientes.add_cliente'

    def get_form_kwargs(self):
        """
        Pasa el freelancer al formulario para que clean_email()
        pueda validar duplicados dentro del mismo freelancer.
        """
        kwargs = super().get_form_kwargs()
        kwargs['freelancer'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Asigna el freelancer autenticado antes de guardar el cliente.
        """
        form.instance.freelancer = self.request.user
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, UpdateView):
    """
    Vista para editar un cliente existente.

    Aplica FreelancerPropietarioMixin para que solo el freelancer
    propietario pueda editar sus clientes.
    Pasa el freelancer al formulario para validar duplicados de email.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'apps/clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    permission_required = 'clientes.change_cliente'

    def get_form_kwargs(self):
        """
        Pasa el freelancer al formulario para que clean_email()
        pueda validar duplicados dentro del mismo freelancer.
        """
        kwargs = super().get_form_kwargs()
        kwargs['freelancer'] = self.request.user
        return kwargs