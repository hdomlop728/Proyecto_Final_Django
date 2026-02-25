from django.urls import path
from . import views

urlpatterns = [
    path('', views.FacturaListView.as_view(), name='factura_list'),
    path('<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('<int:pk>/registrar-pago/', views.registrar_pago, name='factura_registrar_pago'),
    path('<int:pk>/anular/', views.anular_factura, name='factura_anular'),
]