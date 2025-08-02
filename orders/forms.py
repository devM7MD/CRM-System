from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _
from sellers.models import Product

class OrderForm(forms.ModelForm):
    """Form for creating and updating orders."""
    
    class Meta:
        model = Order
        fields = [
            'order_code', 'customer', 'date', 'product', 'quantity',
            'price_per_unit', 'status', 'customer_phone', 'seller_email', 
            'store_link', 'shipping_address', 'city', 'state', 'zip_code', 
            'country', 'notes', 'internal_notes'
        ]
        widgets = {
            'order_code': forms.TextInput(attrs={
                'class': 'form-input w-full bg-gray-50',
                'readonly': 'readonly'
            }),
            'customer': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter customer full name'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-input w-full',
                'type': 'datetime-local'
            }),
            'product': forms.Select(attrs={
                'class': 'form-input w-full product-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'min': '1',
                'step': '1'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-input w-full price-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input w-full'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': '+971501234567'
            }),
            'seller_email': forms.EmailInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'seller@atlasfulfillment.ae'
            }),
            'store_link': forms.URLInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'https://store.atlasfulfillment.ae'
            }),
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-input w-full',
                'rows': '3',
                'placeholder': 'Enter complete shipping address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'State/Province'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'ZIP Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Country'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input w-full',
                'rows': '3',
                'placeholder': 'Customer notes or special instructions'
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'form-input w-full',
                'rows': '3',
                'placeholder': 'Internal notes for team members'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial date to current time if creating new order
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')
        
        # Set seller email based on current user if creating new order
        if not self.instance.pk and user:
            self.fields['seller_email'].initial = user.email
        
        # Populate product choices with real products from database
        products = Product.objects.all().order_by('name_en')
        self.fields['product'].choices = [('', 'Select Product')] + [
            (product.id, f"{product.name_en} - {product.code} (AED {product.selling_price})")
            for product in products
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        
        # Validate price is in AED (positive number)
        price = cleaned_data.get('price_per_unit')
        if price and price <= 0:
            self.add_error('price_per_unit', 'Price must be greater than 0 AED')
        
        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """Form for order items."""
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 
                'min': 1
            }),
            'price': forms.NumberInput(attrs={
                'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 
                'step': '0.01', 
                'min': '0',
                'placeholder': '0.00 AED'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate product choices with real products from database
        products = Product.objects.all().order_by('name_en')
        self.fields['product'].choices = [('', 'Select Product')] + [
            (product.id, f"{product.name_en} - {product.code} (AED {product.selling_price})")
            for product in products
        ]


# Create a formset for order items
OrderItemFormSet = inlineformset_factory(
    Order, 
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)


class OrderStatusUpdateForm(forms.ModelForm):
    """Form for updating order status."""
    
    tracking_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
        })
    )
    
    cancelled_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent',
            'rows': 2
        })
    )
    
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        cancelled_reason = self.data.get('cancelled_reason', '')
        tracking_number = self.data.get('tracking_number', '')
        
        # If status is cancelled, cancelled_reason is required
        if status == 'cancelled' and not cancelled_reason:
            self.add_error('status', 'Cancellation reason is required when status is set to Cancelled')
        
        # If status is in delivery or delivered, tracking_number is required
        if status in ['shipped', 'delivered'] and not tracking_number:
            self.add_error('status', 'Tracking number is required for Delivery statuses')
        
        return cleaned_data 


class OrderImportForm(forms.Form):
    file = forms.FileField(
        label=_('Import File'),
        help_text=_('Upload a CSV or Excel file containing order data.')
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith(('.csv', '.xlsx', '.xls')):
                raise forms.ValidationError(_('File must be CSV or Excel format.'))
        return file

    def save(self):
        file = self.cleaned_data['file']
        # TODO: Implement file parsing and order creation logic
        # This will depend on your specific file format and requirements
        pass 