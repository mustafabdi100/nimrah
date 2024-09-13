# forms.py

from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'street_address_1', 'street_address_2',
            'city', 'state_county', 'phone_number', 'email', 'order_notes'
        ]
        widgets = {
            'street_address_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit etc. (optional)'}),
            'order_notes': forms.Textarea(attrs={'rows': 4}),
        }
