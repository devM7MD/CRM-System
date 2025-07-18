from django import forms
from .models import SourcingRequest


class SourcingRequestForm(forms.ModelForm):
    """Form for creating and editing sourcing requests."""
    
    # Additional fields for the form
    request_type = forms.ChoiceField(
        choices=[
            ('', 'Select a request type'),
            ('new_supplier', 'New Supplier'),
            ('replenishment', 'Inventory Replenishment'),
            ('new_product', 'New Product Sourcing'),
            ('sample', 'Sample Request'),
        ],
        widget=forms.Select(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'required': 'required'
        })
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'required': 'required'
        })
    )
    
    target_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'type': 'date',
            'required': 'required'
        })
    )
    
    budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Enter budget in AED'
        })
    )
    
    product = forms.ChoiceField(
        choices=[('', 'Select a product')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
        })
    )
    
    new_product_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Enter new product name'
        })
    )
    
    references = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'sr-only'
        })
    )
    
    class Meta:
        model = SourcingRequest
        fields = [
            'product_name', 'carton_quantity', 'unit_quantity',
            'source_country', 'destination_country', 'finance_source',
            'supplier_contact', 'supplier_phone', 'cost_per_unit',
            'shipping_cost', 'customs_fees', 'weight', 'dimensions',
            'priority', 'notes'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Enter product name (e.g., iPhone 15 Pro Max)'
            }),
            'carton_quantity': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'min': '1',
                'max': '10000'
            }),
            'unit_quantity': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'min': '1',
                'max': '1000'
            }),
            'source_country': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'destination_country': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'finance_source': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'supplier_contact': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Supplier contact person name'
            }),
            'supplier_phone': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': '+971501234567'
            }),
            'cost_per_unit': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0'
            }),
            'shipping_cost': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0'
            }),
            'customs_fees': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'LxWxH in cm (e.g., 30x20x10)'
            }),
            'priority': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'rows': '4',
                'placeholder': 'Add any additional specifications, requirements, or notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for country fields
        source_countries = [
            ('', 'Select source country'),
            ('China', 'China'),
            ('India', 'India'),
            ('Thailand', 'Thailand'),
            ('Vietnam', 'Vietnam'),
            ('Malaysia', 'Malaysia'),
            ('South Korea', 'South Korea'),
            ('Japan', 'Japan'),
            ('USA', 'USA'),
            ('Germany', 'Germany'),
            ('Italy', 'Italy'),
            ('Other', 'Other'),
        ]
        
        destination_countries = [
            ('', 'Select destination country'),
            ('UAE', 'UAE'),
            ('Saudi Arabia', 'Saudi Arabia'),
            ('Kuwait', 'Kuwait'),
            ('Qatar', 'Qatar'),
            ('Bahrain', 'Bahrain'),
            ('Oman', 'Oman'),
            ('Egypt', 'Egypt'),
            ('Jordan', 'Jordan'),
            ('Lebanon', 'Lebanon'),
            ('Morocco', 'Morocco'),
            ('Other', 'Other'),
        ]
        
        self.fields['source_country'].choices = source_countries
        self.fields['destination_country'].choices = destination_countries
        
        # Set default priority
        self.fields['priority'].initial = 'medium'
    
    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        product = cleaned_data.get('product')
        new_product_name = cleaned_data.get('new_product_name')
        
        # Validate based on request type
        if request_type == 'new_product':
            if not new_product_name:
                raise forms.ValidationError('Product name is required for new product requests.')
        elif request_type in ['replenishment', 'sample']:
            if not product:
                raise forms.ValidationError('Product selection is required for replenishment or sample requests.')
        
        return cleaned_data 