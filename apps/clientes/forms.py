from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """
    Formulario para crear y editar clientes.

    Validaciones:
        - El email no puede estar duplicado dentro del mismo freelancer.
        - Si el cliente tiene usuario asociado, los campos nombre, email
          y estado se ocultan ya que se sincronizan automáticamente.
        - Si el cliente no tiene usuario asociado, nombre y email son obligatorios.
    """

    class Meta:
        model = Cliente
        # El freelancer se asigna automáticamente en la vista con request.user, por lo que no aparece en el formulario.
        fields = ['freelancer', 'usuario_cliente', 'nombre', 'email', 'telefono', 'direccion', 'estado']


        widgets = {
            'freelancer': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecciona un usuario freelancer'
            }),
            'usuario_cliente': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecciona un usuario cliente'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre o razón social'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de contacto'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección',
                'rows': 3
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        kwargs.pop('freelancer', None) extrae el freelancer de los kwargs antes de
        pasárselos a Django. Si no lo extrajéramos, Django lanzaría un error porque
        no reconoce 'freelancer' como un argumento válido del formulario.
        Lo guardamos en self.freelancer para usarlo después en clean_email().
        """
        self.freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)

        # Si el cliente tiene usuario asociado quitamos los campos nombre, email y estado
        if self.instance and self.instance.usuario_cliente:
            del self.fields['nombre']
            del self.fields['email']
            del self.fields['estado']

    def clean_usuario_cliente(self):
        """
        Valida que el usuario cliente sea de tipo cliente.

        Raises:
            ValidationError: Si el usuario no es de tipo cliente.
        """
        usuario_cliente = self.cleaned_data.get('usuario_cliente')
        if usuario_cliente and usuario_cliente.perfil.tipo_cuenta != 'cliente':
            raise forms.ValidationError('El usuario debe ser de tipo cliente.')
        return usuario_cliente

    def clean_nombre(self):
        """
        Valida que el nombre no esté vacío si no hay usuario asociado.

        Raises:
            ValidationError: Si el nombre está vacío y no hay usuario asociado.
        """
        nombre = self.cleaned_data.get('nombre')
        usuario_cliente = self.cleaned_data.get('usuario_cliente')
        if not usuario_cliente and not nombre:
            raise forms.ValidationError('El nombre es obligatorio si no hay usuario asociado.')
        return nombre

    def clean_email(self):
        """
        Valida que el email no esté duplicado dentro del mismo freelancer
        y que no esté vacío si no hay usuario asociado.

        Raises:
            ValidationError: Si el email está vacío o duplicado.
        """
        email = self.cleaned_data.get('email')
        usuario_cliente = self.cleaned_data.get('usuario_cliente')

        if not usuario_cliente and not email:
            raise forms.ValidationError('El email es obligatorio si no hay usuario asociado.')

        """
        La consulta ORM filtra los clientes por el freelancer y por el email
        introducido, excluye al mismo cliente (para no validarse contra sí mismo)
        y devuelve True si hay algún cliente con el mismo email y freelancer, o False si no.
        """
        if self.freelancer and email and Cliente.objects.filter(
            freelancer=self.freelancer,
            email=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un cliente con este email.')
        return email


"""
En la views.py hay que hacer lo siguiente para asignar el freelancer y pasarlo
al formulario:

def form_valid(self, form):
    # Asignamos el freelancer antes de guardar
    form.instance.freelancer = self.request.user
    return super().form_valid(form)

def get_form_kwargs(self):
    # Pasamos el freelancer al formulario para que clean_email pueda validar
    kwargs = super().get_form_kwargs()
    kwargs['freelancer'] = self.request.user
    return kwargs
"""