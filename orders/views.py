"""
Order Views
Checkout process and order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm


def checkout(request):
    """
    Checkout page
    Creates order from cart contents
    """
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        
        if form.is_valid():
            # Create order with transaction to ensure data consistency
            with transaction.atomic():
                # Create order
                order = form.save(commit=False)
                
                # Link to user if authenticated
                if request.user.is_authenticated:
                    order.user = request.user
                
                # Calculate totals
                order.subtotal = cart.get_total_price()
                order.tax = 0  # Add tax calculation if needed
                order.shipping_cost = 0  # Add shipping calculation if needed
                order.total = order.subtotal + order.tax + order.shipping_cost
                
                order.save()
                
                # Create order items from cart
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item['product'].id,
                        product_name=item['product'].name,
                        product_slug=item['product'].slug,
                        price=item['price'],
                        quantity=item['quantity']
                    )
                    
                    # Reduce stock (optional, can be done on payment confirmation)
                    product = item['product']
                    product.stock_quantity -= item['quantity']
                    product.save()
                
                # Clear the cart
                cart.clear()
                
                # Redirect to order confirmation
                return redirect('orders:confirmation', order_number=order.order_number)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })


def order_confirmation(request, order_number):
    """
    Order confirmation page
    Shows order details after successful checkout
    """
    order = get_object_or_404(Order, order_number=order_number)
    
    # Optional: Only allow viewing own orders
    # if request.user.is_authenticated and order.user != request.user:
    #     return redirect('products:home')
    
    return render(request, 'orders/confirmation.html', {
        'order': order
    })


@login_required
def order_list(request):
    """
    User's order history
    Requires authentication
    """
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items').order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_number):
    """
    Individual order details
    Only accessible to order owner
    """
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    
    return render(request, 'orders/order_detail.html', {
        'order': order
    })
