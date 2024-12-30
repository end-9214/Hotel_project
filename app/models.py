from django.db import models
import uuid
from django.conf import settings
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files import File

# Customer Model
class Customer(models.Model):
    ROLES = [
        ('Customer', 'Customer'),
        ('Admin', 'Admin'),
    ]
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=ROLES, default='Customer')
    phone = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

# Table Model
class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        # Generate QR code with URL pointing to login page
        url = f"{settings.BASE_URL}{reverse('qr_code_login')}?table_id={self.id}"
        qrcode_img = qrcode.make(url)
        canvas = BytesIO()
        qrcode_img.save(canvas, format='PNG')
        canvas.seek(0)
        self.qr_code.save(f'qr_code_{self.id}.png', File(canvas), save=False)
        canvas.close()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Table {self.id}"

# Items Model
class Items(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='items', blank=True)

    def __str__(self):
        return self.name

# Order Model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)  # No need for default=None
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True)  # Table is mandatory now
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order {self.id} for {self.customer.username}"

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, null=True)  # No need for default=None
    item = models.ForeignKey(Items, on_delete=models.CASCADE, null=True)  # No need for default=None
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

# ScanRecord Model
class ScanRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.customer.username} scanned at {self.table.id} on {self.scanned_at}"
