"""
Products URL Configuration
Clean, SEO-friendly URL structure
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Product catalog
    path('products/', views.ProductListView.as_view(), name='list'),
    
    # Category pages
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    
    # Product detail
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
]
