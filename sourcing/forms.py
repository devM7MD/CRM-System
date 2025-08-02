from django import forms
from .models import SourcingRequest


class ComprehensiveSourcingForm(forms.Form):
    """Comprehensive sourcing form with all required and optional fields."""
    
    # Required Form Fields
    product_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Enter product name (e.g., iPhone 15 Pro Max)',
            'required': 'required'
        }),
        help_text='Provide clear, specific product name including model numbers if applicable'
    )
    
    carton_quantity = forms.IntegerField(
        min_value=1,
        max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Enter quantity in cartons',
            'required': 'required'
        }),
        help_text='Specify quantity in cartons/boxes. Standard carton sizes vary by product.'
    )
    
    source_country = forms.ChoiceField(
        choices=[
            ('', 'Select source country'),
            ('China', 'China'),
            ('India', 'India'),
            ('Thailand', 'Thailand'),
            ('Vietnam', 'Vietnam'),
            ('Malaysia', 'Malaysia'),
            ('South Korea', 'South Korea'),
            ('Japan', 'Japan'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'required': 'required'
        }),
        help_text='Select the country where you want the product to be sourced from'
    )
    
    destination_country = forms.ChoiceField(
        choices=[
            ('', 'Select destination country'),
            ('UAE', 'UAE'),
            ('Saudi Arabia', 'Saudi Arabia'),
            ('Kuwait', 'Kuwait'),
            ('Qatar', 'Qatar'),
            ('Bahrain', 'Bahrain'),
            ('Oman', 'Oman'),
            ('Egypt', 'Egypt'),
            ('Jordan', 'Jordan'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'required': 'required'
        }),
        help_text='Select the country where the product should be delivered'
    )
    
    funding_source = forms.ChoiceField(
        choices=[
            ('', 'Select funding source'),
            ('seller_funds', "Seller's Funds - I will finance this sourcing request"),
            ('crm_funding', 'CRM Funding Request - Request CRM to finance this sourcing'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'focus:ring-yellow-500 h-4 w-4 text-yellow-600 border-gray-300'
        }),
        help_text='Choose how this sourcing request will be financed'
    )
    
    # Optional Form Fields
    supplier_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Enter preferred supplier name (optional)'
        }),
        help_text='If you have a preferred supplier, provide their company name'
    )
    
    supplier_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': '+971501234567'
        }),
        help_text='Include country code for international numbers'
    )
    
    product_description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'rows': '4',
            'placeholder': 'Enter detailed product specifications and requirements...'
        }),
        help_text='Detailed product specifications and requirements'
    )
    
    target_unit_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'step': '0.01',
            'placeholder': 'Enter target unit price'
        }),
        help_text='Help administrators understand pricing expectations'
    )
    
    currency = forms.ChoiceField(
        choices=[
            ('USD', 'USD'),
            ('AED', 'AED'),
            ('SAR', 'SAR'),
        ],
        required=False,
        initial='AED',
        widget=forms.Select(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md'
        })
    )
    
    quality_requirements = forms.MultipleChoiceField(
        choices=[
            ('brand_new', 'Brand New Only'),
            ('original_packaging', 'Original Packaging Required'),
            ('warranty', 'Warranty Required'),
            ('certified', 'Certified Products Only'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'focus:ring-yellow-500 h-4 w-4 text-yellow-600 border-gray-300 rounded'
        }),
        help_text='Specify quality standards and requirements'
    )
    
    special_instructions = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'shadow-sm focus:ring-yellow-500 focus:border-yellow-500 block w-full sm:text-sm border-gray-300 rounded-md',
            'rows': '3',
            'placeholder': 'Enter additional requirements or special handling instructions...'
        }),
        help_text='Additional requirements or special handling instructions'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that at least one funding source is selected
        funding_source = cleaned_data.get('funding_source')
        if not funding_source:
            raise forms.ValidationError('Please select a funding source.')
        
        # Validate carton quantity
        carton_quantity = cleaned_data.get('carton_quantity')
        if carton_quantity and carton_quantity < 1:
            raise forms.ValidationError('Carton quantity must be at least 1.')
        
        # Validate target unit price if provided
        target_unit_price = cleaned_data.get('target_unit_price')
        if target_unit_price and target_unit_price <= 0:
            raise forms.ValidationError('Target unit price must be greater than 0.')
        
        return cleaned_data


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