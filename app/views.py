from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
import os
import logging
from django.utils import timezone

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
    tables = Table.objects.all()
    return render(request, 'tables.html', {'form': form, 'tables': tables})

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
    orders = Order.objects.filter(table=table).prefetch_related('order_items__item')  # Optimize queries
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
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        item = Items.objects.get(id=item_id)

        customer_id = request.session.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        table = Table.objects.first()  # Replace with appropriate logic if necessary
        
        # Set customer_name to the logged-in customer's username
        order, created = Order.objects.get_or_create(customer_name=customer.username, table=table)
        
        order_item, created = OrderItem.objects.get_or_create(order=order, item=item, defaults={'quantity': quantity})
        if not created:
            order_item.quantity += quantity
            order_item.save()

        return redirect('customer_main')

    items = Items.objects.all()
    return render(request, 'customer_main.html', {'items': items})


def cart(request):
    # Retrieve the table and customer from the session
    table_id = request.session.get('table_id')
    table = get_object_or_404(Table, id=table_id)

    customer_id = request.session.get('customer_id')

    # Get the active order for the customer and table
    orders = Order.objects.filter(customer_name=customer_id, table=table)

    # Pass the orders to the template
    return render(request, 'cart.html', {'orders': orders})