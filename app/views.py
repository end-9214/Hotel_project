from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


# Create your views here.

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