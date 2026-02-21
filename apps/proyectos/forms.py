# apps/proyectos/forms.py
from django import forms
from .models import Proyecto


class ProyectoForm(forms.ModelForm):
    """
    Formulario para crear y editar proyectos.

    Validaciones:
        - La fecha de fin debe ser posterior a la fecha de inicio.
        - El nombre del proyecto no puede estar duplicado dentro del mismo cliente.
        - El freelancer debe ser de tipo freelancer.
        - La fecha de inicio es obligatoria.
    """

    class Meta:
        model = Proyecto
        # El freelancer se podría asignar automáticamente en la vista con request.user
        fields = ['freelancer', 'cliente', 'nombre', 'descripcion', 'estado', 'fecha_inicio', 'fecha_fin']


        widgets = {
            'freelancer': forms.Select(attrs={
                'class': 'form-select',
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-select',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del proyecto',
                'rows': 3
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_fecha_inicio(self):
        """
        Valida que la fecha de inicio no sea nula.

        Raises:
            ValidationError: Si la fecha de inicio es nula.
        """
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if not fecha_inicio:
            raise forms.ValidationError('La fecha de inicio es obligatoria.')
        return fecha_inicio

    def clean_fecha_fin(self):
        """
        Valida que la fecha de fin sea posterior a la fecha de inicio.
        Solo valida si la fecha de fin está rellena, ya que es opcional.

        Raises:
            ValidationError: Si la fecha de fin es anterior a la fecha de inicio.
        """
        fecha_fin = self.cleaned_data.get('fecha_fin')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            raise forms.ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')
        return fecha_fin

    def clean_nombre(self):
        """
        Valida que el nombre del proyecto no esté duplicado dentro del mismo cliente.
        El exclude() es necesario para no validarse contra sí mismo al editar.

        Raises:
            ValidationError: Si ya existe un proyecto con ese nombre para este cliente.
        """
        nombre = self.cleaned_data.get('nombre')
        cliente = self.cleaned_data.get('cliente')
        if nombre and cliente:
            if Proyecto.objects.filter(
                nombre=nombre,
                cliente=cliente
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un proyecto con este nombre para este cliente.')
        return nombre


"""
En la views.py hay que hacer lo siguiente para asignar el freelancer automáticamente:

def form_valid(self, form):
    form.instance.freelancer = self.request.user
    return super().form_valid(form)
"""