"""
Cart Views
Handle add/remove/update operations
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .cart import Cart


def cart_detail(request):
    """Display cart contents"""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """Add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock availability
    if product.stock_quantity < quantity:
        messages.error(request, f'Sorry, only {product.stock_quantity} items available in stock.')
        return redirect('products:detail', slug=product.slug)
    
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'{product.name} added to cart.')
    
    # Redirect to cart or product page based on request
    next_url = request.POST.get('next', 'cart:detail')
    if next_url == 'product':
        return redirect('products:detail', slug=product.slug)
    return redirect('cart:detail')


@require_POST
def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart:detail')


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        # Check stock availability
        if product.stock_quantity < quantity:
            messages.error(request, f'Sorry, only {product.stock_quantity} items available in stock.')
            return redirect('cart:detail')
        
        cart.update_quantity(product_id, quantity)
        messages.success(request, 'Cart updated.')
    else:
        cart.remove(product)
        messages.success(request, f'{product.name} removed from cart.')
    
    return redirect('cart:detail')
