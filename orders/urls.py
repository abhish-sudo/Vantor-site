"""
Orders URL Configuration
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Order confirmation
    path('confirmation/<uuid:order_number>/', views.order_confirmation, name='confirmation'),
    
    # User order history
    path('my-orders/', views.order_list, name='list'),
    
    # Individual order details
    path('<uuid:order_number>/', views.order_detail, name='detail'),

    path('failure/', views.failure, name='failure'),  
    path('success/', views.success, name='success'),
    path("esewa-checkout/<uuid:order_number>/", views.esewa_checkout, name="esewa_checkout"),
    
]
