"""
Product Views
Architecture: Class-based views for consistency and reusability
"""
from django.views.generic import ListView, DetailView
from django.db.models import Q, Prefetch
from .models import Product, Category, ProductImage


class HomeView(ListView):
    """
    Homepage with featured products and hero section
    Optimized queries with select_related and prefetch_related
    """
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        """Get featured and new products with optimized queries"""
        return Product.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_primary=True)
            )
        )[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get new arrivals
        context['new_arrivals'] = Product.objects.filter(
            is_active=True,
            is_new_arrival=True
        ).select_related('category').prefetch_related(
            'images'
        )[:3]
        
        # Get bestsellers
        context['bestsellers'] = Product.objects.filter(
            is_active=True,
            is_bestseller=True
        ).select_related('category').prefetch_related(
            'images'
        )[:3]
        
        return context


class ProductListView(ListView):
    """
    Product catalog with filtering and search
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_primary=True)
            )
        )
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Sort options
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['price', '-price', 'name', '-created_at']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories for filter sidebar
        context['categories'] = Category.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Current category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = Category.objects.get(slug=category_slug)
        
        # Search query
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        return context


class ProductDetailView(DetailView):
    """
    Individual product page with full details
    Optimized query to prevent N+1 problems
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Related products from same category
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(
            pk=self.object.pk
        ).prefetch_related('images')[:4]
        
        return context


class CategoryView(ListView):
    """
    Category-specific product listing
    """
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = Category.objects.get(
            slug=self.kwargs['slug'],
            is_active=True
        )
        return Product.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
