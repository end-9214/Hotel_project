from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Table
from .forms import TableForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import os


# Create your views here.

def customer_login(request):
    return render(request, 'customer_login.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
            orders = Orders.objects.filter(table=table)
                

    return render(request, 'table_details.html', {'orders': orders})
