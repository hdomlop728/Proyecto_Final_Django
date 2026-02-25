from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages

from .models import Factura
from .forms import FacturaForm, PagoForm
from apps.setup.mixins import FreelancerPropietarioMixin, ClientePropietarioMixin


class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'apps/facturas/factura_list.html'
    context_object_name = 'facturas'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name='FREELANCER').exists():
            qs = qs.filter(presupuesto__proyecto__freelancer=user)
        elif user.groups.filter(name='CLIENTE').exists():
            qs = qs.filter(presupuesto__proyecto__cliente__usuario_cliente=user)

        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
            self.request.session['facturas_ultimo_filtro_estado'] = estado
        else:
            estado_sesion = self.request.session.get('facturas_ultimo_filtro_estado')
            if estado_sesion:
                qs = qs.filter(estado=estado_sesion)
        return qs


class FacturaDetailView(LoginRequiredMixin, FreelancerPropietarioMixin, ClientePropietarioMixin, DetailView):
    model = Factura
    template_name = 'apps/facturas/factura_detail.html'
    context_object_name = 'factura'


class RegisterPaymentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'facturas.puede_registrar_pago'

    def get(self, request, pk):
        factura = get_object_or_404(Factura, pk=pk)
        form = PagoForm(factura=factura)
        return render(request, 'apps/facturas/register_payment.html', {'form': form, 'factura': factura})

    def post(self, request, pk):
        factura = get_object_or_404(Factura, pk=pk)
        form = PagoForm(request.POST, factura=factura)
        if form.is_valid():
            factura.registrar_pago(
                cantidad=form.cleaned_data['cantidad'],
                metodo=form.cleaned_data['metodo'],
                notas=form.cleaned_data.get('notas', '')
            )
            messages.success(request, 'Pago registrado correctamente.')
            return redirect('factura_detail', pk=pk)
        return render(request, 'apps/facturas/register_payment.html', {'form': form, 'factura': factura})
