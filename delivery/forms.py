from django import forms
from django.utils.translation import gettext_lazy as _
from .models import DeliveryRecord, DeliveryCompany, Courier, DeliveryStatusHistory, DeliveryRecordEnhanced
from orders.models import Order

class DeliveryRecordSimpleForm(forms.ModelForm):
    """Form for simple delivery records."""
    class Meta:
        model = DeliveryRecord
        fields = [
            'order', 'tracking_number', 'status', 'driver',
            'delivery_notes', 'delivery_cost'
        ]
        widgets = {
            'delivery_notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show orders that don't already have a delivery record
        existing_deliveries = DeliveryRecord.objects.values_list('order_id', flat=True)
        self.fields['order'].queryset = Order.objects.exclude(id__in=existing_deliveries)

class DeliveryRecordEnhancedForm(forms.ModelForm):
    """Form for creating and updating enhanced delivery records."""
    class Meta:
        model = DeliveryRecordEnhanced
        fields = [
            'order', 'tracking_number', 'barcode', 'delivery_company', 
            'courier', 'status', 'priority', 'estimated_delivery',
            'delivery_notes'
        ]
        widgets = {
            'estimated_delivery': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'delivery_notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show orders that don't already have a delivery record
        existing_deliveries = DeliveryRecordEnhanced.objects.values_list('order_id', flat=True)
        self.fields['order'].queryset = Order.objects.exclude(id__in=existing_deliveries)
        # Only show active couriers
        self.fields['courier'].queryset = Courier.objects.filter(status='active')
        # Only show active companies
        self.fields['delivery_company'].queryset = DeliveryCompany.objects.filter(status='active')

class StatusUpdateForm(forms.Form):
    """Form for updating delivery status."""
    STATUS_CHOICES = DeliveryRecordEnhanced.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label=_('Status'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        max_length=255, 
        required=False,
        label=_('Location'),
        widget=forms.TextInput(attrs={'placeholder': _('Current location')})
    )
    notes = forms.CharField(
        required=False,
        label=_('Notes'),
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _('Add notes about this status update')})
    )

class CourierForm(forms.ModelForm):
    """Form for creating and updating couriers."""
    class Meta:
        model = Courier
        fields = [
            'name', 'company', 'phone', 'email', 'status', 
            'available', 'service_areas'
        ]
        widgets = {
            'service_areas': forms.SelectMultiple(attrs={'class': 'select2'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service_areas optional in the form
        if 'service_areas' in self.fields:
            self.fields['service_areas'].required = False

class DeliveryCompanyForm(forms.ModelForm):
    """Form for creating and updating delivery companies."""
    class Meta:
        model = DeliveryCompany
        fields = [
            'name', 'contact_person', 'phone', 'email', 
            'address', 'status'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class AssignmentForm(forms.Form):
    """Form for assigning orders to couriers."""
    order_ids = forms.MultipleChoiceField(
        label=_('Orders'),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    courier = forms.ModelChoiceField(
        queryset=Courier.objects.filter(status='active', available=True),
        label=_('Courier'),
        required=True
    )
    company = forms.ModelChoiceField(
        queryset=DeliveryCompany.objects.filter(status='active'),
        label=_('Delivery Company'),
        required=True
    )
    priority = forms.ChoiceField(
        choices=DeliveryRecordEnhanced.PRIORITY_CHOICES,
        label=_('Priority'),
        initial='normal'
    )
    
    def __init__(self, *args, **kwargs):
        available_orders = kwargs.pop('available_orders', None)
        super().__init__(*args, **kwargs)
        
        if available_orders:
            self.fields['order_ids'].choices = [
                (order.id, f"{order.order_code} - {order.customer.full_name if order.customer else 'Unknown'}")
                for order in available_orders
            ] 