"""
Cart Service
Session-based cart with business logic separation
Architecture: Service pattern for cart operations, easily upgradeable to database-backed cart
"""
from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    """
    Session-based shopping cart
    Design: Can be upgraded to database model for persistent carts later
    """
    
    def __init__(self, request):
        """Initialize the cart from session"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity
        
        Args:
            product: Product instance
            quantity: Quantity to add
            override_quantity: If True, replace quantity instead of adding
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """Mark the session as modified"""
        self.session.modified = True
    
    def remove(self, product):
        """Remove a product from the cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update_quantity(self, product_id, quantity):
        """Update the quantity of a cart item"""
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """
        Iterate over cart items and get products from database
        """
        product_ids = self.cart.keys()
        # Get products and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """Count all items in the cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Calculate total price of all items"""
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def get_item_count(self):
        """Get total number of items (same as __len__)"""
        return len(self)
    
    def clear(self):
        """Remove cart from session"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_items(self):
        """Get all cart items as a list"""
        return list(self.__iter__())
