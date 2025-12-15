from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse



@login_required
def payments(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    # 1) Parse JSON body from PayPal JS
    try:
        body = json.loads(request.body)
        print("DEBUG payments(): body =", body)
    except json.JSONDecodeError as e:
        print("DEBUG payments(): JSON error:", e)
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 2) Get pending order
    try:

        order = Order.objects.get(
            user=request.user,
            is_ordered=False,
            order_number=body["orderID"],
        )
        print("DEBUG payments(): found order =", order.order_number)
    except Order.DoesNotExist:
        print("DEBUG payments(): Order.DoesNotExist")
        return JsonResponse({"error": "Order not found"}, status=404)

    # 3) Create Payment
    payment = Payment.objects.create(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body.get("payment_method", "PayPal"),
        amount_paid=order.order_total,
        status=body.get("status", "COMPLETED"),
    )

    # 4) Mark order as ordered
    order.payment = payment
    order.is_ordered = True
    order.save()
    print("DEBUG payments(): order marked as ordered")

    # 5) Move cart items -> OrderProduct and reduce stock
    cart_items = CartItem.objects.filter(user=request.user)
    print("DEBUG payments(): cart_items count =", cart_items.count())

    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )
        order_product.variations.set(item.variations.all())

        product = item.product
        product.stock -= item.quantity
        product.save()

        print(
            f"DEBUG payments(): created OrderProduct for {product.product_name}, qty={item.quantity}"
        )

    # 6) Clear cart
    cart_items.delete()
    print("DEBUG payments(): cart cleared")

    # 7) Send order received email (do NOT break payments if email fails)
    try:
        to_email = order.email or request.user.email
        mail_subject = "Thank you for your order!"
        mail_body = render_to_string(
            "orders/order_received_email.html",
            {"user": request.user, "order": order},
        )
        email = EmailMessage(
            subject=mail_subject,
            body=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        print("DEBUG payments(): order email sent to:", to_email)
    except Exception as e:
        print("DEBUG payments(): email failed:", e)

    # 8) Return JSON to JS (so JS can redirect to order_complete)
    redirect_url = (
        reverse("order_complete")
        + f"?order_number={order.order_number}&payment_id={payment.payment_id}"
    )

    data = {
        "order_number": order.order_number,
        "payment_id": payment.payment_id,
        "redirect_url": redirect_url,
    }
    print("DEBUG payments(): returning JSON =", data)
    return JsonResponse(data)
# =============================================================


@login_required
def place_order(request: HttpRequest) -> HttpResponse:
    """
    This view:
      - Calculates totals (total, tax, grand_total)
      - Saves an Order record when form is valid
      - Generates order_number
      - Renders orders/payments.html so user can review & pay
    """
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (8.875 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():

            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]

            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            # Generate order number (YYYYMMDD + ID)
            today = datetime.date.today()
            current_date = today.strftime("%Y%m%d")  # e.g. 20251208
            order_number = current_date + str(data.id)  # type: ignore[arg-type]
            data.order_number = order_number
            data.save()

            # Get the fresh order instance
            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )

            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": f"{grand_total:.2f}",
            }
            return render(request, "orders/payments.html", context)

    # If method is not POST or form invalid, go back to checkout
    return redirect("checkout")

# =============================================================

@login_required
def order_complete(request: HttpRequest) -> HttpResponse:
    order_number = request.GET.get("order_number")
    payment_id = request.GET.get("payment_id")

    if not order_number or not payment_id:
        return redirect("home")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=payment_id)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect("home")

    context = {
        "order": order,
        "ordered_products": ordered_products,
        "order_number": order.order_number,
        "transId": payment.payment_id,
        "payment": payment,
        "subtotal": subtotal,
    }
    return render(request, "orders/order_complete.html", context)
