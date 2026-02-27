from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
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

        # Manejo del filtro 'estado' similar a proyectos: si el formulario envía
        # una cadena vacía significa "(todos)" y debemos limpiar la sesión.
        if 'estado' in self.request.GET:
            estado = self.request.GET.get('estado')
            if estado == '':
                self.request.session.pop('facturas_ultimo_filtro_estado', None)
            else:
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

    def get_context_data(self, **kwargs):
        from decimal import Decimal
        context = super().get_context_data(**kwargs)
        factura = self.object
        # calcular total con impuestos y saldo pendiente
        impuestos = factura.presupuesto.impuestos or 0
        total_base = Decimal(factura.presupuesto.total)
        total_con_impuestos = (total_base * (Decimal('1') + Decimal(impuestos) / Decimal('100'))).quantize(Decimal('0.01'))
        pagos_list = []
        for pago in factura.pagos:
            # pagos guardan la cantidad como string en algunos casos
            cantidad = Decimal(pago.get('cantidad', '0'))
            pagos_list.append({
                'fecha': pago.get('fecha'),
                'cantidad': cantidad.quantize(Decimal('0.01')),
                'metodo': pago.get('metodo'),
                'notas': pago.get('notas', ''),
            })
        total_pagado = factura.total_pagado or Decimal('0')
        saldo = (total_con_impuestos - Decimal(total_pagado)).quantize(Decimal('0.01'))
        context.update({
            'total_con_impuestos': total_con_impuestos,
            'total_base': total_base.quantize(Decimal('0.01')),
            'impuestos_percent': impuestos,
            'pagos_list': pagos_list,
            'saldo_pendiente': saldo,
        })
        return context


class FacturaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'apps/facturas/factura_form.html'
    success_url = reverse_lazy('factura_list')
    permission_required = 'facturas.add_factura'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.groups.filter(name='FREELANCER').exists():
            form.fields['presupuesto'].queryset = form.fields['presupuesto'].queryset.filter(
                proyecto__freelancer=user
            )
        return form

    def form_valid(self, form):
        return super().form_valid(form)


class FacturaUpdateView(LoginRequiredMixin, FreelancerPropietarioMixin, ClientePropietarioMixin, PermissionRequiredMixin, UpdateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'apps/facturas/factura_form.html'
    success_url = reverse_lazy('factura_list')
    permission_required = 'facturas.change_factura'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.groups.filter(name='FREELANCER').exists():
            form.fields['presupuesto'].queryset = form.fields['presupuesto'].queryset.filter(
                proyecto__freelancer=user
            )
        return form


class FacturaDeleteView(LoginRequiredMixin, FreelancerPropietarioMixin, ClientePropietarioMixin, PermissionRequiredMixin, DeleteView):
    model = Factura
    template_name = 'apps/facturas/factura_confirm_delete.html'
    success_url = reverse_lazy('factura_list')
    permission_required = 'facturas.delete_factura'


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
