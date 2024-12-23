from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
import uuid

# Create your models here.

class customer(models.Model):
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
        self.qr_code.save(f'qr_code_{self.id}.png', File(canvas), save=False)
        canvas.close()
        super().save(*args, **kwargs)