from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('accounts/register/', views.RegistroView.as_view(), name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('set-theme/', views.set_theme, name='set_theme'),
]