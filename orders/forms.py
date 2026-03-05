"""
Order Forms
Clean checkout form with validation
"""
from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Checkout form for creating orders
    """

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address_line1',
            'address_line2',
            'city',
            'state_province',
            'postal_code',
            'country',
            'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+977 9800000000'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Street Address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'State / Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Special instructions (optional)',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make address_line2, notes optional visually
        self.fields['address_line2'].required = False
        self.fields['notes'].required = False
        self.fields['country'].initial = 'Nepal'
        # Remove verbose labels - placeholders do the job
        for field in self.fields.values():
            field.label = ''

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone