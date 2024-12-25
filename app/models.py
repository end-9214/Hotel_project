from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
import uuid

# Create your models here.

class Customer(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(f'Table ID: {self.id}')
        canvas = BytesIO()
        qrcode_img.save(canvas, format='PNG')
        canvas.seek(0)
        self.qr_code.save(f'qr_code_{self.id}.png', File(canvas), save=False)
        canvas.close()
        super().save(*args, **kwargs)

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    order_items = models.ManyToManyField('OrderItem')
    table = models.ForeignKey(Table, on_delete=models.CASCADE)

class OrderItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name