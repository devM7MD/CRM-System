from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Payment

# Create your views here.

@login_required
def dashboard(request):
    """Finance dashboard with real data."""
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
    # No Expense model, so set expenses to 0 for now
    total_expenses = 0
    net_profit = total_revenue - total_expenses
    pending_payments = Payment.objects.filter(payment_status='pending').count()
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def payment_list(request):
    """List of payments."""
    return render(request, 'finance/payment_list.html')

@login_required
def sales_report(request):
    """Sales reports and analytics."""
    return render(request, 'finance/sales_report.html')
