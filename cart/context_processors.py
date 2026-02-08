"""
Cart Context Processors
Makes cart available in all templates
"""
from .cart import Cart


def cart_context(request):
    """
    Add cart to template context globally
    Allows {{ cart.get_total_price }} in any template
    """
    return {'cart': Cart(request)}
