from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Country, DeliveryCompany, DeliveryArea, SystemFees

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code', 'currency', 'timezone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USA, GBR'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USD, EUR'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., America/New_York, Europe/London'}),
        }
        help_texts = {
            'code': _('ISO 3166-1 alpha-3 country code (3 letters)'),
            'currency': _('ISO 4217 currency code (3 letters)'),
            'timezone': _('IANA timezone identifier'),
        }

class DeliveryCompanyForm(forms.ModelForm):
    class Meta:
        model = DeliveryCompany
        fields = ['name', 'code', 'countries', 'base_cost', 'api_key', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'countries': forms.SelectMultiple(attrs={'class': 'form-control select2', 'multiple': 'multiple'}),
            'base_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'base_cost': _('Default shipping cost for this delivery company'),
            'api_key': _('API key for integration with delivery company (if applicable)'),
        }

class DeliveryAreaForm(forms.ModelForm):
    class Meta:
        model = DeliveryArea
        fields = ['country', 'name', 'code', 'additional_cost']
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control select2'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'additional_cost': _('Additional delivery cost for this area'),
        }

class SystemFeesForm(forms.ModelForm):
    class Meta:
        model = SystemFees
        fields = [
            'upsell_fees', 'confirmation_fees', 'cancellation_fees',
            'fulfillment_fees', 'shipping_fees', 'return_fees', 'warehouse_fees'
        ]
        widgets = {
            'upsell_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'confirmation_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cancellation_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fulfillment_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'shipping_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'return_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'warehouse_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        } 