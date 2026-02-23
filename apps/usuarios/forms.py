from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import re
from .models import Usuario, Perfil


class UsuarioRegistroForm(UserCreationForm):
    """
    Formulario para registrar un nuevo usuario.
    Incluye todos los campos del perfil para crearlo correctamente.

    Campos de Usuario:
        - username, email, password1, password2.
    Campos de Perfil:
        - tipo_cuenta, nif, nombre_fiscal, tema, idioma, formato_nums.
    """
    tipo_cuenta = forms.ChoiceField(
        choices=Perfil.TIPO_CUENTA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nif = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF/CIF'})
    )
    nombre_fiscal = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre fiscal'})
    )
    tema = forms.ChoiceField(
        choices=Perfil.TEMAS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    idioma = forms.ChoiceField(
        choices=Perfil.IDIOMAS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    formato_nums = forms.ChoiceField(
        choices=Perfil.FORMATOS_NUMS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre visible'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }

    def clean_email(self):
        """
        Valida que el email no esté duplicado.
        No hace falta el exclude() porque es un registro nuevo.

        Raises:
            ValidationError: Si ya existe un usuario con ese email.
        """
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este email.')
        return email

    def clean_nif(self):
        """
        Valida el formato del NIF (persona física) o CIF (empresa).
        NIF: 8 números + 1 letra. Ej: 12345678A
        CIF: 1 letra + 7 números + 1 letra o número. Ej: B12345678
        Solo valida si el campo está relleno, ya que es opcional.

        Raises:
            ValidationError: Si el formato del NIF/CIF no es válido.
        """
        nif = self.cleaned_data.get('nif')
        if nif:
            nif_pattern = r'^\d{8}[A-Z]$'
            cif_pattern = r'^[A-Z]\d{7}[A-Z0-9]$'
            if re.match(nif_pattern, nif):
                return nif
            elif re.match(cif_pattern, nif):
                return nif
            else:
                raise forms.ValidationError('El formato del NIF/CIF no es válido. NIF: 12345678A | CIF: B12345678')
        return nif


class UsuarioEdicionForm(UserChangeForm):
    """
    Formulario para editar un usuario existente.
    Hereda de UserChangeForm que ya incluye las validaciones
    de cambio de contraseña por defecto de Django.

    Campos:
        - username: nombre visible del usuario.
        - email: email único del usuario.
        - is_active: estado del usuario (activo/inactivo).
    """
    password = None

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre visible'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_email(self):
        """
        Valida que el email no esté duplicado excluyendo al propio usuario.

        Raises:
            ValidationError: Si ya existe otro usuario con ese email.
        """
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un usuario con este email.')
        return email


class PerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil de un usuario existente.

    Campos:
        - tipo_cuenta: freelancer o cliente.
        - nif: NIF/CIF opcional.
        - nombre_fiscal: nombre fiscal opcional.
        - tema: preferencia de tema visual (claro/oscuro).
        - idioma: preferencia de idioma (es/en).
        - formato_nums: preferencia de formato de números (es/en).
    """
    class Meta:
        model = Perfil
        fields = ['tipo_cuenta', 'nif', 'nombre_fiscal', 'tema', 'idioma', 'formato_nums']
        # El campo perfil (OneToOne con Usuario) se asigna automáticamente en la vista.
        widgets = {
            'tipo_cuenta': forms.Select(attrs={'class': 'form-select'}),
            'nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF/CIF'}),
            'nombre_fiscal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre fiscal'}),
            'tema': forms.Select(attrs={'class': 'form-select'}),
            'idioma': forms.Select(attrs={'class': 'form-select'}),
            'formato_nums': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_nif(self):
        """
        Valida el formato del NIF (persona física) o CIF (empresa).
        NIF: 8 números + 1 letra. Ej: 12345678A
        CIF: 1 letra + 7 números + 1 letra o número. Ej: B12345678
        Solo valida si el campo está relleno, ya que es opcional.

        Raises:
            ValidationError: Si el formato del NIF/CIF no es válido.
        """
        nif = self.cleaned_data.get('nif')
        if nif:
            nif_pattern = r'^\d{8}[A-Z]$'
            cif_pattern = r'^[A-Z]\d{7}[A-Z0-9]$'
            if re.match(nif_pattern, nif):
                return nif
            elif re.match(cif_pattern, nif):
                return nif
            else:
                raise forms.ValidationError('El formato del NIF/CIF no es válido. NIF: 12345678A | CIF: B12345678')
        return nif


"""
En la views.py hay que hacer lo siguiente para crear usuario y perfil juntos:

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
"""