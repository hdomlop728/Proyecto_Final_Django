# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UsuarioRegistroForm
from .models import Perfil
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, 'apps/usuarios/dashboard.html')

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

