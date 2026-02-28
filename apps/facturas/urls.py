from django.urls import path
from . import views

urlpatterns = [
    path('', views.FacturaListView.as_view(), name='factura_list'),
    path('create/', views.FacturaCreateView.as_view(), name='factura_create'),
    path('<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('<int:pk>/edit/', views.FacturaUpdateView.as_view(), name='factura_edit'),
    path('<int:pk>/eliminar/', views.FacturaDeleteView.as_view(), name='factura_delete'),
    path('<int:pk>/register-payment/', views.RegisterPaymentView.as_view(), name='factura_register_payment'),
    path('<int:pk>/pdf/', views.FacturaDescargarPDFView.as_view(), name='factura_pdf'),
]