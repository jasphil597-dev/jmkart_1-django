# carts/context_processors.py

from .models import Cart, CartItem
from .views import cart_id  # make sure this import path is correct


def counter(request):
    cart_count = 0

    # Avoid running this in admin pages
    if "admin" in request.path:
        return {}

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user,
                is_active=True,
            )
        else:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_items = CartItem.objects.filter(
                cart=cart,
                is_active=True,
            )

        for item in cart_items:
            cart_count += item.quantity  # ✅ only quantity, NOT id

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        cart_count = 0

    return dict(cart_count=cart_count)
