from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProyectoListView.as_view(), name='proyecto_list'),
    path('crear/', views.ProyectoCreateView.as_view(), name='proyecto_create'),
    path('<int:pk>/', views.ProyectoDetailView.as_view(), name='proyecto_detail'),
    path('<int:pk>/editar/', views.ProyectoUpdateView.as_view(), name='proyecto_update'),
    path('<int:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='proyecto_delete'),
]