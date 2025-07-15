from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _

class OrderForm(forms.ModelForm):
    """Form for creating and updating orders."""
    
    class Meta:
        model = Order
        fields = [
            'order_code', 'customer', 'product', 'quantity',
            'price_per_unit', 'seller', 'status',
            'customer_phone', 'seller_phone', 'seller_email', 'store_link'
        ]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        postponed_date = cleaned_data.get('postponed_date')
        
        # If status is postponed, postponed_date is required
        if status == 'postponed' and not postponed_date:
            self.add_error('postponed_date', 'Postponed date is required when status is set to Postponed')
        
        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """Form for order items."""
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent'}),
            'quantity': forms.NumberInput(attrs={'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 'step': '0.01', 'min': 0}),
        }


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
            'status': forms.Select(attrs={'class': 'bg-white border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent'}),
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
        if status in ['in_delivery', 'delivered'] and not tracking_number:
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