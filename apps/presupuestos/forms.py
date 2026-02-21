from django import forms
from .models import Presupuesto


class PresupuestoForm(forms.ModelForm):
    """
    Formulario para crear y editar presupuestos.

    Validaciones:
        - La fecha de validez debe ser posterior a la fecha del presupuesto.
        - El total no puede ser negativo.
        - El estado debe ser coherente con las reglas de negocio:
            - No se puede convertir a factura si está en borrador o rechazado.
    """

    class Meta:
        model = Presupuesto
        # numero_serie se genera automáticamente en el save() del modelo.
        exclude = ['numero_serie']


        widgets = {
            'proyecto': forms.Select(attrs={
                'class': 'form-select',
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'validez': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
            }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total sin IVA'
            }),
            'impuestos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'IVA (%)'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales',
                'rows': 3
            }),
        }

    def clean_fecha(self):
        """
        Valida que la fecha no sea nula.

        Raises:
            ValidationError: Si la fecha es nula.
        """
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            raise forms.ValidationError('La fecha es obligatoria.')
        return fecha

    def clean_validez(self):
        """
        Valida que la fecha de validez sea posterior a la fecha del presupuesto.

        Raises:
            ValidationError: Si la fecha de validez es anterior a la fecha del presupuesto.
        """
        validez = self.cleaned_data.get('validez')
        fecha = self.cleaned_data.get('fecha')
        if fecha and validez and validez < fecha:
            raise forms.ValidationError('La fecha de validez no puede ser anterior a la fecha del presupuesto.')
        return validez

    def clean_total(self):
        """
        Valida que el total no sea negativo.

        Raises:
            ValidationError: Si el total es negativo.
        """
        total = self.cleaned_data.get('total')
        if total is not None and total < 0:
            raise forms.ValidationError('El total no puede ser negativo.')
        return total

    def clean_estado(self):
        """
        Valida que el estado sea coherente con las reglas de negocio.
        Si el estado es borrador o rechazado, guarda un atributo para que
        la vista pueda comprobarlo antes de llamar a convertir_a_factura().
        """
        estado = self.cleaned_data.get('estado')
        if estado in ('borrador', 'rechazado'):
            self.instance._estado_invalido_para_convertir = True
        return estado


"""
En la views.py hay que comprobar antes de convertir a factura:

def form_valid(self, form):
    presupuesto = form.instance
    if getattr(presupuesto, '_estado_invalido_para_convertir', False):
        form.add_error('estado', 'No se puede convertir a factura un presupuesto en borrador o rechazado.')
        return self.form_invalid(form)
    return super().form_valid(form)
"""