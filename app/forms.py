from django import forms
from .models import *

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = []

class ItemForm(forms.ModelForm):
    class Meta:
        model = Items
        fields =  ['name', 'price', 'description', 'image']