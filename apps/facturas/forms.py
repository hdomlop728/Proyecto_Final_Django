from django import forms
from .models import Factura
from decimal import Decimal, ROUND_HALF_UP


class FacturaForm(forms.ModelForm):
    """
    Formulario para crear y editar facturas.

    Validaciones:
        - La fecha de vencimiento debe ser posterior a la fecha de emisión.
        - El estado debe ser coherente con las reglas de negocio.
        - La factura no puede editarse si está anulada.
        - El presupuesto debe estar en estado aceptado.
    """

    class Meta:
        model = Factura
        # numero_serie se genera automáticamente en el save() del modelo.
        # pagos se gestiona a través del metodo registrar_pago() del modelo.
        # total_pagado se actualiza automáticamente mediante F expressions en registrar_pago() del modelo.
        exclude = ['numero_serie', 'pagos', 'total_pagado']


        widgets = {
            'presupuesto': forms.Select(attrs={
                'class': 'form-select',
            }),
            'fecha_emision': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_fecha_vencimiento(self):
        """
        Valida que la fecha de vencimiento sea posterior a la fecha de emisión.

        Raises:
            ValidationError: Si la fecha de vencimiento es anterior a la fecha de emisión.
        """
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        fecha_emision = self.cleaned_data.get('fecha_emision')
        if fecha_emision and fecha_vencimiento and fecha_vencimiento < fecha_emision:
            raise forms.ValidationError('La fecha de vencimiento no puede ser anterior a la fecha de emisión.')
        return fecha_vencimiento

    def clean_estado(self):
        """
        Valida que el estado sea coherente con las reglas de negocio:
            - Una factura anulada no puede cambiar de estado.
            - Una factura pagada no puede volver a pendiente o parcial.

        Raises:
            ValidationError: Si el estado no es coherente.
        """
        estado = self.cleaned_data.get('estado')
        if self.instance.pk:
            estado_actual = self.instance.estado
            if estado_actual == 'anulada':
                raise forms.ValidationError('Una factura anulada no puede cambiar de estado.')
            if estado_actual == 'pagada' and estado in ('pendiente', 'parcial'):
                raise forms.ValidationError('Una factura pagada no puede volver a pendiente o parcial.')
        return estado

    def clean_presupuesto(self):
        """
        Valida que el presupuesto esté en estado aceptado para poder
        generar una factura a partir de él.

        Raises:
            ValidationError: Si el presupuesto no está aceptado.
        """
        presupuesto = self.cleaned_data.get('presupuesto')
        if presupuesto and presupuesto.estado != 'aceptado':
            raise forms.ValidationError('Solo se puede generar una factura desde un presupuesto aceptado.')
        return presupuesto


class PagoForm(forms.Form):
    """
    Formulario para registrar un pago en una factura.

    Validaciones:
        - La cantidad debe ser mayor que cero.
        - La cantidad no puede superar el total pendiente de la factura.
        - La factura no puede estar anulada o pagada.
        - El metodo de pago es obligatorio.
        - Las notas son opcionales.
    La actualización del estado a parcial/pagada se gestiona en
    el metodo registrar_pago() del modelo.
    """

    # Como es un forms.Form y no un forms.ModelForm, los widgets deben ir como atributos

    METODOS_PAGO = (
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('efectivo', 'Efectivo'),
        ('bizum', 'Bizum'),
    )


    cantidad = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Cantidad a abonar',
                'step': '0.01',
            }
        )
    )
    metodo = forms.ChoiceField(
        choices=METODOS_PAGO,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Notas opcionales',
                'rows': 3
            }
        )
    )

    def __init__(self, *args, **kwargs):
        # Extraemos la factura de los kwargs igual que hicimos con el freelancer en ClienteForm
        self.factura = kwargs.pop('factura', None)
        super().__init__(*args, **kwargs)

    def clean_cantidad(self):
        """
        Valida que la cantidad no sea negativa y que no supere el total pendiente.

        Raises:
            ValidationError: Si la cantidad es negativa, cero o supera el total pendiente.
        """
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        if self.factura:
            total_con_impuestos = (self.factura.presupuesto.total * (1 + self.factura.presupuesto.impuestos / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_pagado = self.factura.total_pagado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            pendiente = (total_con_impuestos - total_pagado).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if cantidad > pendiente:
                raise forms.ValidationError(f'La cantidad supera el total pendiente ({pendiente:.2f}).')

        return cantidad

    def clean(self):
        """
        Valida que la factura permita registrar pagos según su estado actual.

        Raises:
            ValidationError: Si la factura está anulada o ya está pagada.
        """
        cleaned_data = super().clean()
        if self.factura:
            if self.factura.estado == 'anulada':
                raise forms.ValidationError('No se puede registrar un pago en una factura anulada.')
            if self.factura.estado == 'pagada':
                raise forms.ValidationError('La factura ya está completamente pagada.')
        return cleaned_data

"""
En la views.py hay que hacer lo siguiente:

Para FacturaForm:
def form_valid(self, form):
    # La factura se crea desde convertir_a_factura() del presupuesto, no directamente
    return super().form_valid(form)

Para PagoForm:
def post(self, request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    form = PagoForm(request.POST, factura=factura)  # hay que pasar la factura al formulario
    if form.is_valid():
        factura.registrar_pago(
            cantidad=form.cleaned_data['cantidad'],
            metodo=form.cleaned_data['metodo'],
            notas=form.cleaned_data.get('notas', '')
        )
    return redirect('factura_detail', pk=pk)
"""
