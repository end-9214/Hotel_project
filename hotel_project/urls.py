from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admins', user_login, name='login'),
    path('dashboard', dashboard, name='dashboard'),
    path('', client_login, name='client_login'),
    path('tables/', tables, name='tables'),
    path('delete/<uuid:id>/', delete_table, name='delete_table'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)