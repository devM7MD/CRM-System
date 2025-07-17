from django import forms
from django.utils.translation import gettext_lazy as _
from .models import BugReport

class BugReportForm(forms.ModelForm):
    class Meta:
        model = BugReport
        fields = ['title', 'description', 'priority', 'page_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Brief description of the bug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full resize-none',
                'rows': 4,
                'placeholder': 'Detailed description of the bug, steps to reproduce, and expected behavior...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-input w-full'
            }),
            'page_url': forms.URLInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'https://example.com/page-where-bug-occurs'
            }),
        } 