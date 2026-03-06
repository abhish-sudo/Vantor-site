"""
Order Views
Checkout process and order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
import hmac
import hashlib
import base64
import json
from decimal import Decimal
import os
import stripe
import urllib.request
from django.core.cache import cache


# ═════════════════════════════════════════════
# CHECKOUT
# ═════════════════════════════════════════════

def checkout(request):
    """
    Renders checkout form and creates the Order in DB.
    Cart is NOT cleared here — only cleared after payment is confirmed.
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
                order.status = 'pending'

                # Don't set payment_method yet — user picks on next page
                order.payment_method = ''
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

                # Clean up old unpaid pending orders for this user (avoid clutter)
                if request.user.is_authenticated:
                    Order.objects.filter(
                        user=request.user,
                        status='pending',
                        is_paid=False,
                    ).exclude(order_number=order.order_number).delete()

                # ✅ Cart is NOT cleared here — cleared only after payment confirmed
                # Redirect to payment selection page
                return redirect('orders:payment_selection', order_number=order.order_number)

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

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


# ═════════════════════════════════════════════
# PAYMENT SELECTION
# ═════════════════════════════════════════════

@login_required
def payment_selection(request, order_number):
    """
    Shows all available payment methods.
    Handles COD directly. Stripe and eSewa redirect to their own views.
    Add new payment methods here in the future.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Already paid — go to success
    if order.is_paid:
        return redirect('orders:success_page', order_number=order.order_number)

    if request.method == 'POST':
        selected = request.POST.get('payment_method')

        if selected == 'cod':
            with transaction.atomic():
                order.payment_method = 'cod'
                order.status = 'processing'  # ✅ confirmed but not yet paid
                order.is_paid = False         # ✅ not paid until delivery
                # Don't set paid_at — they haven't paid yet
                order.save()
                _reduce_stock(order)

            cart = Cart(request)
            cart.clear()

            return redirect('orders:success_page', order_number=order.order_number)

    return render(request, 'orders/payment_selection.html', {'order': order})


# ═════════════════════════════════════════════
# UNIVERSAL SUCCESS & FAILURE PAGES
# ═════════════════════════════════════════════

def success_page(request, order_number):
    """
    Universal success page for ALL payment methods (eSewa, Stripe, COD).
    Template reads order.payment_method to show the right message.
    """
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/success.html', {'order': order})


def failure_page(request, order_number=None):
    """
    Universal failure/cancel page for ALL payment methods.
    order_number is optional — when present, user can retry payment.
    """
    order = None
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            pass
    return render(request, 'orders/failure.html', {'order': order})


# ═════════════════════════════════════════════
# ORDER MANAGEMENT
# ═════════════════════════════════════════════

def order_confirmation(request, order_number):
    """Backwards compatibility — redirects to success page."""
    return redirect('orders:success_page', order_number=order_number)


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.status not in ['pending', 'paid', 'processing']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:list')

    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock only if order was paid
            if order.is_paid:
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


# ═════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════

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
    """Generate HMAC-SHA256 signature for eSewa."""
    h = hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(h.digest()).decode('utf-8')


def _verify_esewa_signature(payment_data, secret_key):
    """Verify eSewa's response signature. Returns True if valid."""
    signed_field_names = payment_data.get('signed_field_names', '')
    received_signature = payment_data.get('signature', '')

    if not signed_field_names or not received_signature:
        return False

    fields = [f.strip() for f in signed_field_names.split(',')]
    message = ','.join([f"{field}={payment_data.get(field, '')}" for field in fields])
    expected_signature = _generate_esewa_signature(secret_key, message)
    return hmac.compare_digest(expected_signature, received_signature)


def get_npr_to_usd_rate():
    """
    Fetches real-time NPR → USD exchange rate.
    - Free API, no key needed
    - Cached for 1 hour to avoid hitting API on every checkout
    - Falls back to safe hardcoded rate if API is down
    """
    CACHE_KEY = 'npr_usd_rate'
    FALLBACK_RATE = Decimal('0.0075')  # ~133 NPR per 1 USD
    CACHE_TIMEOUT = 60 * 60  # 1 hour

    cached = cache.get(CACHE_KEY)
    if cached:
        return Decimal(str(cached))

    try:
        url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/npr.json'
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            rate = Decimal(str(data['npr']['usd']))
            cache.set(CACHE_KEY, str(rate), CACHE_TIMEOUT)
            return rate
    except Exception:
        return FALLBACK_RATE


# ═════════════════════════════════════════════
# ESEWA
# ═════════════════════════════════════════════

def esewa_checkout(request, order_number):
    """Renders eSewa payment page with signed form data."""
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('products:home')

    if order.is_paid:
        return redirect('orders:success_page', order_number=order.order_number)

    secret_key = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    product_code = os.getenv('ESEWA_PRODUCT_CODE', 'EPAYTEST')
    transaction_uuid = str(order.order_number).replace('-', '')
    total_amount = str(Decimal(str(order.total)).quantize(Decimal('0.01')))

    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = _generate_esewa_signature(secret_key, data_to_sign)

    # Set payment method when user is sent to eSewa
    if order.payment_method != 'esewa':
        order.payment_method = 'esewa'
        order.save(update_fields=['payment_method'])

    return render(request, 'orders/esewa_payment.html', {
        'order': order,
        'tax_amount': '0.00',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'signature': signature,
    })


def esewa_success(request):
    """
    eSewa success callback.
    Verifies signature → marks order paid → clears cart → success page.
    """
    data_param = request.GET.get('data')

    if not data_param:
        messages.error(request, 'No payment data received.')
        return redirect('orders:failure_page_no_order')

    try:
        payment_data = json.loads(base64.b64decode(data_param).decode('utf-8'))
    except Exception:
        messages.error(request, 'Invalid payment response.')
        return redirect('orders:failure_page_no_order')

    secret_key = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    if not _verify_esewa_signature(payment_data, secret_key):
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('orders:failure_page_no_order')

    if payment_data.get('status') != 'COMPLETE':
        messages.error(request, 'Payment was not completed.')
        return redirect('orders:failure_page_no_order')

    transaction_uuid = payment_data.get('transaction_uuid', '')
    try:
        uid = transaction_uuid
        formatted_uuid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:]}"
        order = Order.objects.get(order_number=formatted_uuid)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('orders:failure_page_no_order')

    # Prevent double processing
    if order.is_paid:
        return redirect('orders:success_page', order_number=order.order_number)

    with transaction.atomic():
        order.is_paid = True
        order.status = 'paid'
        order.payment_id = payment_data.get('transaction_code', '')
        order.payment_method = 'esewa'
        order.paid_at = timezone.now()
        order.save()
        _reduce_stock(order)

    # ✅ Clear cart after eSewa payment confirmed
    cart = Cart(request)
    cart.clear()

    return redirect('orders:success_page', order_number=order.order_number)


def esewa_failure(request):
    """eSewa failure/cancel callback."""
    return redirect('orders:failure_page_no_order')


# ═════════════════════════════════════════════
# STRIPE
# ═════════════════════════════════════════════

@login_required
def stripe_payment_page(request, order_number):
    """
    Renders stripe_payment.html — the order summary page
    shown before the user is redirected to Stripe.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.is_paid:
        return redirect('orders:success_page', order_number=order.order_number)

    # Set payment method when user lands on stripe page
    if order.payment_method != 'stripe':
        order.payment_method = 'stripe'
        order.save(update_fields=['payment_method'])

    return render(request, 'orders/stripe_payment.html', {'order': order})


@login_required
def stripe_checkout(request, order_number):
    """
    Creates a Stripe Checkout Session and redirects user to Stripe's hosted page.
    Uses real-time NPR → USD conversion.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = get_object_or_404(Order, order_number=order_number)

    if order.is_paid:
        return redirect('orders:success_page', order_number=order.order_number)

    npr_to_usd = get_npr_to_usd_rate()

    line_items = []
    for item in order.items.all():
        price_usd = item.price * npr_to_usd
        unit_amount = max(int(price_usd * 100), 50)  # Stripe minimum is 50 cents
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': unit_amount,
                'product_data': {
                    'name': item.product_name,
                    'description': f'NPR {item.price} (1 NPR = ${npr_to_usd:.6f} USD)',
                },
            },
            'quantity': item.quantity,
        })

    success_url = (
        request.build_absolute_uri(reverse('orders:stripe_success'))
        + '?session_id={CHECKOUT_SESSION_ID}'
    )
    cancel_url = request.build_absolute_uri(
        reverse('orders:stripe_cancel', kwargs={'order_number': order.order_number})
    )

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
        metadata={
            'order_number': str(order.order_number),
            'order_id': order.id,
            'npr_to_usd_rate': str(npr_to_usd),
        }
    )

    return redirect(session.url, code=303)


def stripe_success(request):
    """
    Stripe redirects user here after payment.
    We just retrieve the order and go to success page.
    Actual order marking is done in the webhook (more reliable).
    """
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('orders:failure_page_no_order')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order_number = session.metadata.get('order_number')
        order = get_object_or_404(Order, order_number=order_number)
        return redirect('orders:success_page', order_number=order.order_number)
    except Exception:
        return redirect('orders:failure_page_no_order')


def stripe_cancel(request, order_number):
    """
    User cancelled/went back on Stripe's page.
    Order stays in DB as pending — user can retry or choose different payment.
    Cart is also still intact so user can go back and add more items.
    """
    return redirect('orders:failure_page_with_order', order_number=order_number)


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe calls this endpoint after a successful payment.
    This is the ONLY place we mark the order as paid for Stripe.
    Signature is verified to prevent fake requests.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        if session.get('payment_status') == 'paid':
            order_number = session['metadata'].get('order_number')

            try:
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            # Prevent double processing
            if not order.is_paid:
                with transaction.atomic():
                    order.is_paid = True
                    order.status = 'paid'
                    order.payment_method = 'stripe'
                    order.payment_id = session.get('payment_intent', '')
                    order.paid_at = timezone.now()
                    order.save()
                    _reduce_stock(order)

                # Clear cart from user's active session after Stripe payment
                if order.user:
                    try:
                        from django.contrib.sessions.models import Session
                        from django.utils import timezone as tz
                        for sess in Session.objects.filter(expire_date__gte=tz.now()):
                            data = sess.get_decoded()
                            if data.get('_auth_user_id') == str(order.user.id):
                                if 'cart' in data:
                                    from django.contrib.sessions.backends.db import SessionStore
                                    store = SessionStore(session_key=sess.session_key)
                                    del store['cart']
                                    store.save()
                                    break
                    except Exception:
                        pass  # Cart clear is best-effort in webhook context

    return HttpResponse(status=200)