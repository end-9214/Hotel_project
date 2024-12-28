from django import template

register = template.Library()

@register.filter
def total_price(order_items):
    """
    Calculate the total price of all items in an order.
    """
    return sum(item.price * item.quantity for item in order_items)
