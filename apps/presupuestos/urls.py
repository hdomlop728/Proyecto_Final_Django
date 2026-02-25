from django.urls import path
from . import views

urlpatterns = [
    path('', views.PresupuestoListView.as_view(), name='presupuesto_list'),
    path('crear/', views.PresupuestoCreateView.as_view(), name='presupuesto_create'),
    path('<int:pk>/', views.PresupuestoDetailView.as_view(), name='presupuesto_detail'),
    path('<int:pk>/editar/', views.PresupuestoUpdateView.as_view(), name='presupuesto_update'),
    path('<int:pk>/eliminar/', views.PresupuestoDeleteView.as_view(), name='presupuesto_delete'),
    path('<int:pk>/convertir/', views.convertir_a_factura, name='presupuesto_convertir'),
]