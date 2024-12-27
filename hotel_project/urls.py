from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admins', user_login, name='login'),
    path('dashboard', dashboard, name='dashboard'),
    path('login/', customer_login, name='client_login'),
    path('tables/', tables, name='tables'),
    path('delete/<uuid:id>/', delete_table, name='delete_table'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('tables/table_details/<uuid:id>', table_details, name = 'table_details'),
    path('menu/', menu, name='menu'),
    path(' ', customer_main, name='customer_main'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)