from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Proyecto
from .forms import ProyectoForm
from apps.setup.mixins import FreelancerPropietarioMixin, ClientePropietarioMixin


class ProyectoListView(LoginRequiredMixin, ListView):
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_list.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # filtrar por propietario según rol
        if user.groups.filter(name='FREELANCER').exists():
            qs = qs.filter(freelancer=user)
        elif user.groups.filter(name='CLIENTE').exists():
            qs = qs.filter(cliente__usuario_cliente=user)

        # aplicar filtrado por estado y guardar en sesión para persistencia
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
            self.request.session['proyectos_ultimo_filtro_estado'] = estado
        else:
            estado_sesion = self.request.session.get('proyectos_ultimo_filtro_estado')
            if estado_sesion:
                qs = qs.filter(estado=estado_sesion)
        return qs


class ProyectoDetailView(LoginRequiredMixin, FreelancerPropietarioMixin, ClientePropietarioMixin, DetailView):
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'


class ProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'apps/proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.add_proyecto'

    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        return super().form_valid(form)


class ProyectoUpdateView(LoginRequiredMixin, FreelancerPropietarioMixin, PermissionRequiredMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'apps/proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.change_proyecto'

    def form_valid(self, form):
        # freelancer no debe cambiar
        return super().form_valid(form)


class ProyectoDeleteView(LoginRequiredMixin, FreelancerPropietarioMixin, PermissionRequiredMixin, DeleteView):
    model = Proyecto
    template_name = 'apps/proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_list')
    permission_required = 'proyectos.delete_proyecto'
