from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('admins', user_login, name='login'),
    path('dashboard', dashboard, name='dashboard'),
]
