from django.db import models

# Create your models here.

class customer(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class table(models.Model):
    table_no = models.IntegerField()
    no_of_seats = models.IntegerField()
    scanned_time = models.DateTimeField(auto_now_add=True)
    exited_time = models.DateTimeField(auto_now=True)