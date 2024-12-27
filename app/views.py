from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
import os


# Create your views here.

def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            customer = Customer.objects.get(username = username)
            if customer.password == password:
                auth_login(request, customer)
                return redirect('customer_main')
            else:
                return HttpResponse("Invalid credentials")
        except Customer.DoesNotExist:
            return HttpResponse("User does not exist")

    return render(request, 'customer_login.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return render(request, 'dashboard.html')
        else:
            return HttpResponse("Invalid login")

    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
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

@login_required
def delete_table(request, id):
    if request.method == 'POST':
        table = get_object_or_404(Table, id=id)
        qr_code_path = table.qr_code.path if table.qr_code else None
        table.delete()
        if qr_code_path and os.path.exists(qr_code_path):
            os.remove(qr_code_path)
        else:
            print(f"The file {qr_code_path} does not exist")
        return redirect('tables')
    return JsonResponse({'error': 'Invalid request'}, status=400)


    
def table_details(request,id):
    if request.method == 'POST':
            table = get_object_or_404(Table, id=id)
            orders = Order.objects.filter(table=table)
            order_items = OrderItem.objects.all()
                

    return render(request, 'table_details.html', {'orders': orders, 'order_items': order_items})


@login_required
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

@login_required
def customer_main(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        item = Items.objects.get(id=item_id)

        order, created = Order.objects.get_or_create(customer_name=request.user.username, table=None)

        order_item, created = OrderItem.objects.get_or_create(order=order, item=item, defaults={'quantity': quantity})
        if not created:
            order_item.quantity += quantity
            order_item.save()

        return redirect('customer_main')

    items = Items.objects.all()
    return render(request, 'customer_main.html', {'items': items})