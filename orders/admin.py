"""
Order Admin
Enhanced admin for order management
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'get_total']
    can_delete = False
    
    def get_total(self, obj):
        return f"NPR {obj.total_price:.2f}"
    get_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'full_name',
        'email',
        'total',
        'status_badge',
        'is_paid',
        'created_at'
    ]
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = [
        'order_number',
        'email',
        'first_name',
        'last_name',
        'phone'
    ]
    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'paid_at',
        'shipped_at',
        'delivered_at',
        'subtotal',
        'tax',
        'shipping_cost',
        'total'
    ]
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'user')
        }),
        ('Customer Information', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'address_line1',
                'address_line2',
                'city',
                'state_province',
                'postal_code',
                'country'
            )
        }),
        ('Order Details', {
            'fields': ('notes',)
        }),
        ('Pricing', {
            'fields': (
                'subtotal',
                'tax',
                'shipping_cost',
                'total'
            )
        }),
        ('Payment Information', {
            'fields': (
                'is_paid',
                'payment_method',
                'payment_id'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'paid_at',
                'shipped_at',
                'delivered_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'processing': '#2196F3',
            'shipped': '#9C27B0',
            'delivered': '#4CAF50',
            'cancelled': '#F44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#777'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = 'Mark as Delivered'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'get_total']
    list_filter = ['order__created_at']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['order', 'product_name', 'price', 'quantity']
    
    def get_total(self, obj):
        return f"NPR {obj.total_price:.2f}"
    get_total.short_description = 'Total'
