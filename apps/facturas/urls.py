from django.urls import path
from . import views

urlpatterns = [
    path('', views.FacturaListView.as_view(), name='factura_list'),
    path('<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('<int:pk>/register-payment/', views.RegisterPaymentView.as_view(), name='factura_register_payment'),
]