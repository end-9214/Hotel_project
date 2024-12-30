from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from .forms import *
from django.contrib.auth.hashers import check_password
import os
import logging
from django.utils import timezone
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            customer = Customer.objects.get(username=username)
            if check_password(password, customer.password):
                request.session['customer_id'] = customer.id
                request.session['customer_role'] = customer.role
                if customer.role == 'Admin':
                    return redirect('dashboard')
                else:
                    return redirect('customer_main')
            else:
                return HttpResponse("Invalid credentials")
        except Customer.DoesNotExist:
            return HttpResponse("User does not exist")

    return render(request, 'customer_login.html')


def qr_code_login(request):
    table = None  # Initialize table to avoid UnboundLocalError

    # Get table_id from the GET parameters
    table_id = request.GET.get('table_id')
    if table_id:
        try:
            # Attempt to retrieve the table using the table_id
            table = get_object_or_404(Table, id=table_id)
            # Store table_id in session for later use
            request.session['table_id'] = table_id
        except Table.DoesNotExist:
            return HttpResponse("Table not found")

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            customer = Customer.objects.get(username=username)
            if check_password(password, customer.password):
                # Save customer data in the session
                request.session['customer_id'] = customer.id
                request.session['customer_role'] = customer.role

                # Record the scan if a table is associated
                if table:
                    ScanRecord.objects.create(
                        customer=customer,
                        table=table,
                        scanned_at=timezone.now()
                    )

                # Redirect to the main customer page
                return redirect('customer_main')
            else:
                return HttpResponse("Invalid credentials")
        except Customer.DoesNotExist:
            return HttpResponse("User does not exist")

    return render(request, 'qr_code_login.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def tables(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tables')
    else:
        form = TableForm()
    tables_list = Table.objects.all()
    return render(request, 'tables.html', {'form': form, 'tables': tables_list})


def delete_table(request, id):
    if request.method == 'POST':
        table = get_object_or_404(Table, id=id)
        qr_code_path = table.qr_code.path if table.qr_code else None
        table.delete()
        if qr_code_path and os.path.exists(qr_code_path):
            os.remove(qr_code_path)
        else:
            logger.warning(f"The file {qr_code_path} does not exist")
        return redirect('tables')
    return JsonResponse({'error': 'Invalid request'}, status=400)


def table_details(request, id):
    table = get_object_or_404(Table, id=id)
    orders = Order.objects.filter(table=table).prefetch_related('order_items__item')
    return render(request, 'table_details.html', {'orders': orders})


def menu(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('menu')
    else:
        form = ItemForm()
    items = Items.objects.all()
    return render(request, 'menu.html', {'form': form, 'items': items})


def customer_main(request):
    if request.method == 'POST':
        # Use item_id for Items since that's the primary key
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        item = Items.objects.get(item_id=item_id)

        # Retrieve the logged-in customer
        customer_id = request.session.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)

        # You can customize table logic as needed
        table = Table.objects.first()

        # Create or get an Order with the customer/table
        order, created = Order.objects.get_or_create(
            customer=customer,
            table=table
        )

        # Create or update the corresponding OrderItem
        order_item, oi_created = OrderItem.objects.get_or_create(
            order=order,
            item=item,
            defaults={'quantity': quantity}
        )
        if not oi_created:
            order_item.quantity += quantity
            order_item.save()

        return redirect('customer_main')

    items_list = Items.objects.all()
    return render(request, 'customer_main.html', {'items': items_list})


def cart(request):
    from django.shortcuts import get_object_or_404
    table_id = request.session.get('table_id')
    table = get_object_or_404(Table, id=table_id)

    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)

    orders = Order.objects.filter(customer=customer, table=table).prefetch_related('order_items__item')

    # Compute total in Python
    total_due = 0
    for order in orders:
        for item in order.order_items.all():
            total_due += item.total_price

    return render(request, 'cart.html', {
        'orders': orders,
        'total_due': total_due,
    })


@require_POST
def cart_update_item(request):
    from django.shortcuts import redirect, get_object_or_404
    from .models import OrderItem

    order_item_id = request.POST.get('order_item_id')
    action = request.POST.get('action', '')

    order_item = get_object_or_404(OrderItem, id=order_item_id)

    if action == 'increment':
        order_item.quantity += 1
        order_item.save()
    elif action == 'decrement':
        # If more than 1, decrement. Otherwise, delete the item.
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()

    return redirect('cart')

def finalize_order(request, order_id):
    """
    Finalizes the order with the given order_id. 
    You can perform payment processing, order confirmation, etc.
    """
    from django.shortcuts import get_object_or_404, redirect
    order = get_object_or_404(Order, id=order_id)

    # Example logic: mark order as finalized or do some other processing
    # order.finalized = True
    # order.save()

    # Redirect to a confirmation page or wherever needed
    return redirect('cart')