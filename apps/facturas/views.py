from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Factura
from .forms import PagoForm
from apps.setup.mixins import FreelancerPropietarioMixin


class FacturaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar las facturas del freelancer autenticado.

    Usa select_related para evitar N+1 al acceder a presupuesto,
    proyecto y cliente desde el template.
    Permite filtrar por estado usando Q objects para combinar
    facturas pendientes O vencidas en un solo filtro.
    """
    model = Factura
    template_name = 'apps/facturas/factura_list.html'
    context_object_name = 'facturas'
    permission_required = 'facturas.view_factura'

    def get_queryset(self):
        """
        Filtra las facturas del freelancer autenticado.
        - select_related: carga presupuesto, proyecto y cliente en una
          sola consulta para evitar N+1 al iterar en el template.
        - Q objects: permite filtrar por (pendiente O vencida) en un
          solo filtro, combinando condiciones de forma eficiente.
        """
        queryset = Factura.objects.filter(
            presupuesto__proyecto__freelancer=self.request.user
        ).select_related(
            'presupuesto__proyecto__cliente'
        )

        busqueda = self.request.GET.get('busqueda', '')
        estado = self.request.GET.get('estado', '')

        if busqueda:
            # Q objects: busca por número de serie O por nombre de cliente
            queryset = queryset.filter(
                Q(numero_serie__icontains=busqueda) |
                Q(presupuesto__proyecto__cliente__nombre__icontains=busqueda)
            )

        if estado == 'pendiente_o_vencida':
            # Q objects: facturas pendientes O vencidas en una sola consulta
            queryset = queryset.filter(
                Q(estado='pendiente') | Q(estado='vencida')
            )
        elif estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['estados'] = Factura.ESTADOS
        return context


class FacturaDetailView(LoginRequiredMixin, PermissionRequiredMixin, FreelancerPropietarioMixin, DetailView):
    """
    Vista para ver el detalle de una factura con su historial de pagos.

    Usa select_related para cargar todas las relaciones en una sola consulta,
    evitando N+1 al acceder a presupuesto, proyecto y cliente en el template.
    """
    model = Factura
    template_name = 'apps/facturas/factura_detail.html'
    context_object_name = 'factura'
    permission_required = 'facturas.view_factura'

    def get_queryset(self):
        """
        - select_related: carga presupuesto, proyecto, cliente y freelancer
          en una sola consulta para evitar N+1 en el template.
        """
        return Factura.objects.select_related(
            'presupuesto__proyecto__cliente',
            'presupuesto__proyecto__freelancer'
        )

    def get_context_data(self, **kwargs):
        """
        Añade el formulario de pago al contexto para mostrarlo
        directamente en el detalle de la factura.
        """
        context = super().get_context_data(**kwargs)
        context['pago_form'] = PagoForm(factura=self.object)
        return context


@login_required
@permission_required('facturas.puede_registrar_pago', raise_exception=True)
def registrar_pago(request, pk):
    """
    Vista FBV para registrar un pago en una factura.

    Solo acepta POST para evitar registros accidentales por GET.
    Comprueba que la factura pertenece al freelancer autenticado.
    Delega la lógica de pago al método registrar_pago() del modelo,
    que usa F expressions para actualizar total_pagado en la BD.

    Args:
        request: La petición HTTP.
        pk: La clave primaria de la factura.
    """
    factura = get_object_or_404(
        Factura,
        pk=pk,
        presupuesto__proyecto__freelancer=request.user
    )

    if request.method == 'POST':
        form = PagoForm(request.POST, factura=factura)
        if form.is_valid():
            try:
                factura.registrar_pago(
                    cantidad=form.cleaned_data['cantidad'],
                    metodo=form.cleaned_data['metodo'],
                    notas=form.cleaned_data.get('notas', '')
                )
                messages.success(request, 'Pago registrado correctamente.')
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return redirect('factura_detail', pk=pk)


@login_required
@permission_required('facturas.puede_anular_factura', raise_exception=True)
def anular_factura(request, pk):
    """
    Vista FBV para anular una factura.

    Solo acepta POST para evitar anulaciones accidentales por GET.
    Comprueba que la factura pertenece al freelancer autenticado.
    La validación de que no se puede anular una factura ya pagada
    se gestiona en el clean() del modelo.

    Args:
        request: La petición HTTP.
        pk: La clave primaria de la factura a anular.
    """
    factura = get_object_or_404(
        Factura,
        pk=pk,
        presupuesto__proyecto__freelancer=request.user
    )

    if request.method == 'POST':
        try:
            factura.estado = 'anulada'
            factura.full_clean()
            factura.save()
            messages.success(request, f'Factura {factura.numero_serie} anulada correctamente.')
        except ValidationError as e:
            messages.error(request, e.message)

    return redirect('factura_detail', pk=pk)