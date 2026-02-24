# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, F
from django.utils import timezone

from .forms import UsuarioRegistroForm
from .models import Perfil
from apps.clientes.models import Cliente
from apps.presupuestos.models import Presupuesto
from apps.facturas.models import Factura


@login_required
def dashboard(request):
    """
    Vista FBV del dashboard financiero del freelancer.

    Muestra métricas globales y por periodo usando aggregate y annotate.
    Los filtros de periodo y cliente se guardan en sesión para que persistan
    entre visitas (requisito de sesión del enunciado).

    Métricas incluidas:
        - Total facturado, cobrado y pendiente (aggregate).
        - Facturas por estado (aggregate + Q objects).
        - Clientes con total facturado (annotate).
        - Alertas de facturas vencidas y presupuestos caducados.
    """

    # ---------------------------------------------------------------
    # SESIÓN: guardamos y recuperamos los filtros de periodo y cliente
    # Se escriben cuando el usuario envía el formulario de filtros (GET)
    # Se leen en cada visita al dashboard
    # Se borran si el usuario pulsa "Limpiar filtros"
    # ---------------------------------------------------------------
    if request.GET.get('limpiar'):
        request.session.pop('dashboard_año', None)
        request.session.pop('dashboard_cliente_id', None)
        return redirect('dashboard')

    if 'año' in request.GET:
        request.session['dashboard_año'] = request.GET.get('año')
    if 'cliente_id' in request.GET:
        request.session['dashboard_cliente_id'] = request.GET.get('cliente_id')

    # Leemos los filtros de la sesión
    año_filtro = request.session.get('dashboard_año', '')
    cliente_id_filtro = request.session.get('dashboard_cliente_id', '')

    # ---------------------------------------------------------------
    # BASE QUERYSETS del freelancer autenticado
    # select_related para evitar N+1 al acceder a relaciones en el template
    # ---------------------------------------------------------------
    facturas_qs = Factura.objects.filter(
        presupuesto__proyecto__freelancer=request.user
    ).select_related('presupuesto__proyecto__cliente')

    presupuestos_qs = Presupuesto.objects.filter(
        proyecto__freelancer=request.user
    ).select_related('proyecto__cliente')

    # ---------------------------------------------------------------
    # FILTROS opcionales por año y cliente (Q objects para combinarlos)
    # ---------------------------------------------------------------
    if año_filtro:
        facturas_qs = facturas_qs.filter(fecha_emision__year=año_filtro)
        presupuestos_qs = presupuestos_qs.filter(fecha__year=año_filtro)

    if cliente_id_filtro:
        facturas_qs = facturas_qs.filter(
            presupuesto__proyecto__cliente__id=cliente_id_filtro
        )
        presupuestos_qs = presupuestos_qs.filter(
            proyecto__cliente__id=cliente_id_filtro
        )

    # ---------------------------------------------------------------
    # AGGREGATE: métricas globales del periodo filtrado
    # ---------------------------------------------------------------
    total_facturado = facturas_qs.exclude(
        estado='anulada'
    ).aggregate(
        total=Sum('presupuesto__total')
    )['total'] or 0

    total_cobrado = facturas_qs.filter(
        estado='pagada'
    ).aggregate(
        total=Sum('total_pagado')
    )['total'] or 0

    total_pendiente = facturas_qs.filter(
        # Q objects: facturas pendientes O parcialmente pagadas
        Q(estado='pendiente') | Q(estado='parcial')
    ).aggregate(
        total=Sum(F('presupuesto__total') - F('total_pagado'))
    )['total'] or 0

    # Conteo de facturas por estado (aggregate)
    facturas_por_estado = {
        'pendiente': facturas_qs.filter(estado='pendiente').count(),
        'parcial':   facturas_qs.filter(estado='parcial').count(),
        'pagada':    facturas_qs.filter(estado='pagada').count(),
        'vencida':   facturas_qs.filter(estado='vencida').count(),
        'anulada':   facturas_qs.filter(estado='anulada').count(),
    }

    # ---------------------------------------------------------------
    # ANNOTATE: clientes con total facturado y número de proyectos
    # Enriquece el queryset con datos calculados sin hacer N+1
    # ---------------------------------------------------------------
    clientes_con_totales = Cliente.objects.filter(
        freelancer=request.user
    ).annotate(
        total_facturado=Sum(
            'proyectos__presupuesto__factura__presupuesto__total',
        ),
        num_proyectos=Count('proyectos', distinct=True),
    ).order_by('-total_facturado')[:5]

    # ---------------------------------------------------------------
    # ALERTAS: facturas vencidas y presupuestos sin convertir caducados
    # Q objects para combinar condiciones en una sola consulta
    # ---------------------------------------------------------------
    facturas_vencidas = Factura.objects.filter(
        presupuesto__proyecto__freelancer=request.user,
        estado='vencida'
    ).count()

    presupuestos_caducados = Presupuesto.objects.filter(
        proyecto__freelancer=request.user,
        validez__lt=timezone.now().date(),
        # Q objects: no aceptados NI rechazados (aún pendientes de gestión)
        estado__in=['borrador', 'enviado']
    ).count()

    # ---------------------------------------------------------------
    # DATOS para los selectores de filtro
    # ---------------------------------------------------------------
    años_disponibles = Factura.objects.filter(
        presupuesto__proyecto__freelancer=request.user
    ).dates('fecha_emision', 'year', order='DESC')

    clientes_disponibles = Cliente.objects.filter(
        freelancer=request.user,
        estado=True
    ).order_by('nombre')

    context = {
        # Métricas financieras
        'total_facturado': total_facturado,
        'total_cobrado': total_cobrado,
        'total_pendiente': total_pendiente,
        'facturas_por_estado': facturas_por_estado,
        # Ranking de clientes
        'clientes_con_totales': clientes_con_totales,
        # Alertas
        'facturas_vencidas': facturas_vencidas,
        'presupuestos_caducados': presupuestos_caducados,
        # Filtros activos (leídos de sesión)
        'año_filtro': año_filtro,
        'cliente_id_filtro': cliente_id_filtro,
        # Datos para los selectores
        'años_disponibles': años_disponibles,
        'clientes_disponibles': clientes_disponibles,
    }

    return render(request, 'apps/usuarios/dashboard.html', context)


def landing(request):
    """
    Vista pública de acceso al sistema.

    Redirige al dashboard si el usuario ya está autenticado.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


class RegistroView(CreateView):
    """
    Vista para registrar un nuevo usuario.

    Crea el perfil asociado automáticamente tras el registro.
    """
    form_class = UsuarioRegistroForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        usuario = form.save()
        Perfil.objects.create(
            perfil=usuario,
            tipo_cuenta=form.cleaned_data['tipo_cuenta'],
            nif=form.cleaned_data.get('nif'),
            nombre_fiscal=form.cleaned_data.get('nombre_fiscal'),
            tema=form.cleaned_data['tema'],
            idioma=form.cleaned_data['idioma'],
            formato_nums=form.cleaned_data['formato_nums'],
        )
        return super().form_valid(form)