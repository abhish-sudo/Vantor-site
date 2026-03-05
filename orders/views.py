"""
Order Views
Checkout process and order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
import hmac
import hashlib
import base64
import json
from decimal import Decimal
import os


def checkout(request):
    """
    Checkout page — handles both eSewa and Cash on Delivery
    """
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)

                if request.user.is_authenticated:
                    order.user = request.user

                order.subtotal = cart.get_total_price()
                order.tax = Decimal('0.00')
                order.shipping_cost = Decimal('0.00')
                order.total = order.subtotal + order.tax + order.shipping_cost

                payment_method = request.POST.get('payment_method', 'esewa')
                order.payment_method = payment_method
                order.status = 'pending'
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item['product'].id,
                        product_name=item['product'].name,
                        product_slug=item['product'].slug,
                        price=item['price'],
                        quantity=item['quantity']
                    )

                cart.clear()

                if payment_method == 'esewa':
                    return redirect('orders:esewa_checkout', order_number=order.order_number)
                else:
                    # COD — reduce stock immediately
                    _reduce_stock(order)
                    return redirect('orders:confirmation', order_number=order.order_number)

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
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
    Order confirmation page — shown after both eSewa and COD orders
    """
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    return render(request, 'orders/order_detail.html', {'order': order})


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _reduce_stock(order):
    """Reduce product stock for all items in an order."""
    from products.models import Product
    for item in order.items.all():
        try:
            product = Product.objects.get(id=item.product_id)
            product.stock_quantity -= item.quantity
            product.save()
        except Product.DoesNotExist:
            pass


def _generate_esewa_signature(key, message):
    """Generate HMAC-SHA256 signature for eSewa"""
    h = hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(h.digest()).decode('utf-8')


def _verify_esewa_signature(payment_data, secret_key):
    """
    Verify the signature eSewa sends back.
    Returns True if valid, False if tampered or invalid.
    """
    signed_field_names = payment_data.get('signed_field_names', '')
    received_signature = payment_data.get('signature', '')

    if not signed_field_names or not received_signature:
        return False

    fields = [f.strip() for f in signed_field_names.split(',')]
    message = ','.join([f"{field}={payment_data.get(field, '')}" for field in fields])
    expected_signature = _generate_esewa_signature(secret_key, message)
    return hmac.compare_digest(expected_signature, received_signature)


# ─────────────────────────────────────────────
# eSewa Views
# ─────────────────────────────────────────────

def esewa_checkout(request, order_number):
    """eSewa payment page"""
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('products:home')

    if order.is_paid:
        return redirect('orders:confirmation', order_number=order.order_number)

    secret_key = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    product_code = os.getenv('ESEWA_PRODUCT_CODE', 'EPAYTEST')
    transaction_uuid = str(order.order_number).replace('-', '')
    total_amount = str(Decimal(str(order.total)).quantize(Decimal('0.01')))

    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = _generate_esewa_signature(secret_key, data_to_sign)

    return render(request, 'orders/esewa_payment.html', {
        'order': order,
        'tax_amount': '0.00',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'signature': signature,
    })


def success(request):
    """
    eSewa success callback — verifies payment then redirects to confirmation.
    eSewa sends: ?data=<base64 encoded JSON>
    """
    data_param = request.GET.get('data')

    if not data_param:
        messages.error(request, 'No payment data received.')
        return redirect('products:home')

    # Decode base64 JSON
    try:
        payment_data = json.loads(base64.b64decode(data_param).decode('utf-8'))
    except Exception:
        messages.error(request, 'Invalid payment response.')
        return redirect('products:home')

    # Verify eSewa's signature
    secret_key = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    if not _verify_esewa_signature(payment_data, secret_key):
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('products:home')

    # Check status is COMPLETE
    if payment_data.get('status') != 'COMPLETE':
        messages.error(request, 'Payment was not completed.')
        return redirect('products:home')

    # Find the order
    transaction_uuid = payment_data.get('transaction_uuid', '')
    try:
        uid = transaction_uuid
        formatted_uuid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:]}"
        order = Order.objects.get(order_number=formatted_uuid)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('products:home')

    # Prevent double processing
    if order.is_paid:
        return redirect('orders:confirmation', order_number=order.order_number)

    # Mark paid + reduce stock atomically
    with transaction.atomic():
        order.is_paid = True
        order.status = 'paid'
        order.payment_id = payment_data.get('transaction_code', '')
        order.payment_method = 'esewa'
        order.paid_at = timezone.now()
        order.save()
        _reduce_stock(order)

    return redirect('orders:confirmation', order_number=order.order_number)


def failure(request):
    """eSewa payment failure callback"""
    return render(request, 'orders/failure.html')


@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Only allow cancelling pending or cod orders
    if order.status not in ['pending', 'paid']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:list')

    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock
            from products.models import Product
            for item in order.items.all():
                try:
                    product = Product.objects.get(id=item.product_id)
                    product.stock_quantity += item.quantity
                    product.save()
                except Product.DoesNotExist:
                    pass

            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order {order.order_number} has been cancelled.')

    return redirect('orders:list')