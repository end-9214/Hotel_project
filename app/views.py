from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Table
from .forms import TableForm
from django.contrib.auth import authenticate, login


# Create your views here.

def client_login(request):
    return render(request, 'client_login.html')

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