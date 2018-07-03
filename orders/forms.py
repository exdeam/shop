from django import forms
from django.forms import TextInput
from .models import Order



class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'postal_code', 'city', 'address']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Пушкин Александр Сергеевич'}),
            'email': TextInput(attrs={'placeholder': 'mypost@mail.ru'}),
            'phone': TextInput(attrs={'placeholder': '7 (123) 456 7890'}),
            'postal_code': TextInput(attrs={'placeholder': '123456'}),
        }
