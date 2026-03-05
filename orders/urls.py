"""
Orders URL Configuration
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<uuid:order_number>/', views.order_confirmation, name='confirmation'),
    path('esewa_payment/<uuid:order_number>/', views.esewa_checkout, name='esewa_checkout'),
    path('success/', views.success, name='success'),
    path('failure/', views.failure, name='failure'),
    path('my-orders/', views.order_list, name='list'),
    path('<uuid:order_number>/', views.order_detail, name='detail'),  # keep last!
]
