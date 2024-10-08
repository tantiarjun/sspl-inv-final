# inventory/forms.py

from django import forms
from .models import Item
from .models import Supplier
from django.core.exceptions import ValidationError
import re

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'category', 'unit_price', 'image']
        widgets ={
            'unit_price':forms.NumberInput(attrs={
                'min':'0'
            })
        }

    # Custom validation for unit_price field
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')

        # Check if unit_price is a valid number
        if unit_price is None:
            raise ValidationError("Unit price is required.")

        # Ensure the value is positive
        if unit_price <= 0:
            raise ValidationError("Unit price must be a positive number.")
        
        # Check if it's not a string (like alphabets or special characters)
        if not isinstance(unit_price, (int, float)):
            raise ValidationError("Unit price must be a valid number.")

        return unit_price
        

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'phone_no', 'address']
        
    
    # Custom validation for phone_no field
    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')

        # Ensure the value is not empty
        if not phone_no:
            raise ValidationError("Phone number is required.")

        # Ensure phone number contains only digits (optional: allow + at the start for country code)
        if not re.match(r'^\+?\d{10,15}$', phone_no):
            raise ValidationError("Enter a valid phone number with 10-15 digits. It may include an optional country code (+).")

        # Example: If you want to enforce local phone numbers starting with certain digits (e.g., for a country)
        if len(phone_no) == 10 and not phone_no.startswith(('7', '8', '9')):
            raise ValidationError("Phone number must start with 7, 8, or 9 for a valid local number.")
        
        
        return phone_no