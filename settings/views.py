from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db import transaction
import json

from .models import Country, DeliveryCompany, DeliveryArea, SystemFees, AuditLog
from .forms import CountryForm, DeliveryCompanyForm, DeliveryAreaForm, SystemFeesForm
from users.models import User

def is_admin(user):
    """Check if user is an admin"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def settings_dashboard(request):
    """Main settings dashboard view"""
    countries_count = Country.objects.count()
    active_countries = Country.objects.filter(is_active=True).count()
    
    delivery_companies_count = DeliveryCompany.objects.count()
    active_delivery_companies = DeliveryCompany.objects.filter(is_active=True).count()
    
    users_count = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Get system fees
    system_fees = SystemFees.get_default_fees()
    
    # Get recent audit logs
    recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'countries_count': countries_count,
        'active_countries': active_countries,
        'delivery_companies_count': delivery_companies_count,
        'active_delivery_companies': active_delivery_companies,
        'users_count': users_count,
        'active_users': active_users,
        'system_fees': system_fees,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'settings/dashboard.html', context)

# Country Management Views
@login_required
@user_passes_test(is_admin)
def country_list(request):
    """List all countries"""
    countries = Country.objects.all().order_by('name')
    
    context = {
        'countries': countries,
    }
    
    return render(request, 'settings/country_list.html', context)

@login_required
@user_passes_test(is_admin)
def country_create(request):
    """Create a new country"""
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            country = form.save()
            
            # Log the creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                table='Country',
                record_id=country.id,
                new_value=json.dumps({field: str(getattr(country, field)) for field in form.fields}),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, _('Country was created successfully.'))
            return redirect('settings:country_list')
    else:
        form = CountryForm()
    
    context = {
        'form': form,
        'title': _('Add Country'),
    }
    
    return render(request, 'settings/country_form.html', context)

@login_required
@user_passes_test(is_admin)
def country_edit(request, pk):
    """Edit an existing country"""
    country = get_object_or_404(Country, pk=pk)
    
    if request.method == 'POST':
        old_values = {field: str(getattr(country, field)) for field in CountryForm.Meta.fields}
        
        form = CountryForm(request.POST, instance=country)
        if form.is_valid():
            country = form.save()
            
            # Log the update
            new_values = {field: str(getattr(country, field)) for field in form.fields}
            AuditLog.objects.create(
                user=request.user,
                action='update',
                table='Country',
                record_id=country.id,
                old_value=json.dumps(old_values),
                new_value=json.dumps(new_values),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, _('Country was updated successfully.'))
            return redirect('settings:country_list')
    else:
        form = CountryForm(instance=country)
    
    context = {
        'form': form,
        'title': _('Edit Country'),
        'country': country,
    }
    
    return render(request, 'settings/country_form.html', context)

@login_required
@user_passes_test(is_admin)
def country_delete(request, pk):
    """Delete a country"""
    country = get_object_or_404(Country, pk=pk)
    
    if request.method == 'POST':
        # Log the deletion
        old_values = {field: str(getattr(country, field)) for field in CountryForm.Meta.fields}
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            table='Country',
            record_id=country.id,
            old_value=json.dumps(old_values),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        country.delete()
        messages.success(request, _('Country was deleted successfully.'))
        return redirect('settings:country_list')
    
    context = {
        'country': country,
    }
    
    return render(request, 'settings/country_confirm_delete.html', context)

# Delivery Company Management Views
@login_required
@user_passes_test(is_admin)
def delivery_company_list(request):
    """List all delivery companies"""
    companies = DeliveryCompany.objects.all().order_by('name')
    
    context = {
        'companies': companies,
    }
    
    return render(request, 'settings/delivery_company_list.html', context)

@login_required
@user_passes_test(is_admin)
def delivery_company_create(request):
    """Create a new delivery company"""
    if request.method == 'POST':
        form = DeliveryCompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            
            # Log the creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                table='DeliveryCompany',
                record_id=company.id,
                new_value=json.dumps({field: str(getattr(company, field)) for field in form.fields if field != 'countries'}),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, _('Delivery company was created successfully.'))
            return redirect('settings:delivery_company_list')
    else:
        form = DeliveryCompanyForm()
    
    context = {
        'form': form,
        'title': _('Add Delivery Company'),
    }
    
    return render(request, 'settings/delivery_company_form.html', context)

@login_required
@user_passes_test(is_admin)
def delivery_company_edit(request, pk):
    """Edit an existing delivery company"""
    company = get_object_or_404(DeliveryCompany, pk=pk)
    
    if request.method == 'POST':
        old_values = {field: str(getattr(company, field)) for field in DeliveryCompanyForm.Meta.fields if field != 'countries'}
        old_values['countries'] = list(company.countries.values_list('id', flat=True))
        
        form = DeliveryCompanyForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save()
            
            # Log the update
            new_values = {field: str(getattr(company, field)) for field in form.fields if field != 'countries'}
            new_values['countries'] = list(company.countries.values_list('id', flat=True))
            
            AuditLog.objects.create(
                user=request.user,
                action='update',
                table='DeliveryCompany',
                record_id=company.id,
                old_value=json.dumps(old_values),
                new_value=json.dumps(new_values),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, _('Delivery company was updated successfully.'))
            return redirect('settings:delivery_company_list')
    else:
        form = DeliveryCompanyForm(instance=company)
    
    context = {
        'form': form,
        'title': _('Edit Delivery Company'),
        'company': company,
    }
    
    return render(request, 'settings/delivery_company_form.html', context)

@login_required
@user_passes_test(is_admin)
def delivery_company_delete(request, pk):
    """Delete a delivery company"""
    company = get_object_or_404(DeliveryCompany, pk=pk)
    
    if request.method == 'POST':
        # Log the deletion
        old_values = {field: str(getattr(company, field)) for field in DeliveryCompanyForm.Meta.fields if field != 'countries'}
        old_values['countries'] = list(company.countries.values_list('id', flat=True))
        
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            table='DeliveryCompany',
            record_id=company.id,
            old_value=json.dumps(old_values),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        company.delete()
        messages.success(request, _('Delivery company was deleted successfully.'))
        return redirect('settings:delivery_company_list')
    
    context = {
        'company': company,
    }
    
    return render(request, 'settings/delivery_company_confirm_delete.html', context)

# Fees Management View
@login_required
@user_passes_test(is_admin)
def fees_management(request):
    """Manage system fees"""
    system_fees = SystemFees.get_default_fees()
    
    if request.method == 'POST':
        old_values = {field: str(getattr(system_fees, field)) for field in SystemFeesForm.Meta.fields}
        
        form = SystemFeesForm(request.POST, instance=system_fees)
        if form.is_valid():
            with transaction.atomic():
                system_fees = form.save(commit=False)
                system_fees.updated_by = request.user
                system_fees.save()
                
                # Log the update
                new_values = {field: str(getattr(system_fees, field)) for field in form.fields}
                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    table='SystemFees',
                    record_id=system_fees.id,
                    old_value=json.dumps(old_values),
                    new_value=json.dumps(new_values),
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
                
                messages.success(request, _('System fees were updated successfully.'))
                return redirect('settings:fees_management')
    else:
        form = SystemFeesForm(instance=system_fees)
    
    context = {
        'form': form,
        'system_fees': system_fees,
    }
    
    return render(request, 'settings/fees_management.html', context)

# User Management Views - Redirect to Users app views if they exist
@login_required
@user_passes_test(is_admin)
def user_management(request):
    """Redirect to Users management app if it exists"""
    return redirect('users:user_list')
