"""
Product Models
Architecture: Designed for future expansion (variants, inventory management, multi-warehouse)
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Product categories with hierarchical support
    Future: Can be extended to support nested categories
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category', args=[self.slug])


class Product(models.Model):
    """
    Core Product Model
    Design decisions:
    - Soft delete (is_active) for historical order integrity
    - Decimal prices for accuracy
    - Slug-based URLs for SEO
    - Ready for variants (size, color) via future ProductVariant model
    """
    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    
    # Product Details
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    benefits = models.TextField(
        blank=True,
        help_text="Key benefits, one per line"
    )
    ingredients = models.TextField(
        blank=True,
        help_text="Product ingredients"
    )
    how_to_use = models.TextField(
        blank=True,
        help_text="Usage instructions"
    )
    
    # Pricing & Inventory
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Original price for sale display"
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Product Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    
    # SEO & Marketing
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.short_description and self.description:
            self.short_description = self.description[:300]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])
    
    @property
    def is_in_stock(self):
        """Check if product is available"""
        return self.stock_quantity > 0
    
    @property
    def is_on_sale(self):
        """Check if product has a discounted price"""
        return self.compare_at_price and self.compare_at_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return int(discount)
        return 0
    
    def get_main_image(self):
        """Get the primary product image"""
        main_image = self.images.filter(is_primary=True).first()
        if main_image:
            return main_image
        return self.images.first()


class ProductImage(models.Model):
    """
    Product images with ordering support
    Allows multiple images per product for gallery views
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='products/%Y/%m/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
