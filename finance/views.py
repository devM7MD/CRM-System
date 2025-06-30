from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.db.models import F, Sum
from django.template.loader import render_to_string
from .models import OrderPayment, OrderFees
from orders.models import Order
from sellers.models import Seller
from inventory.models import Warehouse

@login_required
def finance_list(request):
    """Display list of orders with payment information."""
    orders = Order.objects.select_related(
        'seller', 'fees'
    ).prefetch_related('items', 'payments')
    
    # Apply filters
    seller_id = request.GET.get('seller')
    if seller_id:
        orders = orders.filter(seller_id=seller_id)
    
    status = request.GET.get('status')
    if status:
        orders = orders.filter(payments__payment_status=status)
    
    context = {
        'orders': orders,
        'sellers': Seller.objects.all(),
    }
    return render(request, 'finance/finance_list.html', context)

@login_required
def add_payment(request):
    """Add new payment for orders."""
    if request.method == 'POST':
        seller_id = request.POST.get('seller')
        warehouse_id = request.POST.get('warehouse')
        order_ids = request.POST.getlist('order_ids')
        payment_method = request.POST.get('payment_method')
        payment_status = request.POST.get('payment_status')
        
        try:
            # Create payments for selected orders
            for order_id in order_ids:
                order = Order.objects.get(id=order_id)
                
                # Create or update payment
                payment = OrderPayment.objects.create(
                    order=order,
                    payment_status=payment_status,
                    payment_method=payment_method,
                    amount=float(request.POST.get(f'amount_{order_id}', order.quantity * order.price_per_unit)),
                    transaction_id=request.POST.get('transaction_id', ''),
                    notes=request.POST.get('notes', ''),
                )
                
                # Update or create fees
                fees_data = {
                    'upsell_fees': request.POST.get(f'upsell_fees_{order_id}', 0),
                    'confirmation_fees': request.POST.get(f'confirmation_fees_{order_id}', 0),
                    'cancellation_fees': request.POST.get(f'cancellation_fees_{order_id}', 0),
                    'fulfillment_fees': request.POST.get(f'fulfillment_fees_{order_id}', 0),
                    'shipping_fees': request.POST.get(f'shipping_fees_{order_id}', 0),
                    'return_fees': request.POST.get(f'return_fees_{order_id}', 0),
                    'warehouse_fees': request.POST.get(f'warehouse_fees_{order_id}', 0),
                }
                
                OrderFees.objects.update_or_create(
                    order=order,
                    defaults=fees_data
                )
            
            messages.success(request, _('Payments recorded successfully.'))
            return redirect('finance:finance_list')
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('finance:add_payment')
    
    # Get all sellers and active warehouses for the form
    sellers = Seller.objects.all().select_related('user')
    warehouses = Warehouse.objects.filter(is_active=True)
    
    # Debug information
    seller_count = sellers.count()
    warehouse_count = warehouses.count()
    
    if seller_count == 0:
        messages.warning(request, _('No sellers found in the system. Please add sellers first.'))
    
    if warehouse_count == 0:
        messages.warning(request, _('No active warehouses found. Please add warehouses first.'))
    
    context = {
        'sellers': sellers,
        'warehouses': warehouses,
        'seller_count': seller_count,
        'warehouse_count': warehouse_count,
    }
    return render(request, 'finance/add_payment.html', context)

@login_required
def get_seller_orders(request):
    """API endpoint to get orders for a specific seller."""
    seller_id = request.GET.get('seller')
    warehouse_id = request.GET.get('warehouse')
    
    orders = Order.objects.filter(seller_id=seller_id)
    if warehouse_id:
        orders = orders.filter(warehouse_id=warehouse_id)
    
    orders = orders.select_related('seller', 'fees').prefetch_related('items')
    
    data = [{
        'id': order.id,
        'code': order.code,
        'date': order.date.strftime('%Y-%m-d'),
        'products': [{'name': item.product.name_en, 'quantity': item.quantity, 'price': float(item.price)} 
                    for item in order.items.all()],
        'total_price': float(order.get_total_price()),
        'fees': {
            'upsell': float(order.fees.upsell_fees) if hasattr(order, 'fees') else 0,
            'confirmation': float(order.fees.confirmation_fees) if hasattr(order, 'fees') else 0,
            'cancellation': float(order.fees.cancellation_fees) if hasattr(order, 'fees') else 0,
            'fulfillment': float(order.fees.fulfillment_fees) if hasattr(order, 'fees') else 0,
            'shipping': float(order.fees.shipping_fees) if hasattr(order, 'fees') else 0,
            'return': float(order.fees.return_fees) if hasattr(order, 'fees') else 0,
            'warehouse': float(order.fees.warehouse_fees) if hasattr(order, 'fees') else 0,
        }
    } for order in orders]
    
    return JsonResponse({'orders': data})

@login_required
def update_fees(request, order_id):
    """Update fees for a specific order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            fees_data = {
                'upsell_fees': request.POST.get('upsell_fees', 0),
                'confirmation_fees': request.POST.get('confirmation_fees', 0),
                'cancellation_fees': request.POST.get('cancellation_fees', 0),
                'fulfillment_fees': request.POST.get('fulfillment_fees', 0),
                'shipping_fees': request.POST.get('shipping_fees', 0),
                'return_fees': request.POST.get('return_fees', 0),
                'warehouse_fees': request.POST.get('warehouse_fees', 0),
            }
            
            OrderFees.objects.update_or_create(
                order=order,
                defaults=fees_data
            )
            
            return JsonResponse({
                'success': True,
                'message': _('Fees updated successfully.'),
                'total_fees': float(sum(float(v) for v in fees_data.values()))
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # For GET requests, return current fees
    try:
        fees = OrderFees.objects.get(order=order)
        return JsonResponse({
            'success': True,
            'fees': {
                'upsell': float(fees.upsell_fees),
                'confirmation': float(fees.confirmation_fees),
                'cancellation': float(fees.cancellation_fees),
                'fulfillment': float(fees.fulfillment_fees),
                'shipping': float(fees.shipping_fees),
                'return': float(fees.return_fees),
                'warehouse': float(fees.warehouse_fees),
            }
        })
    except OrderFees.DoesNotExist:
        return JsonResponse({
            'success': True,
            'fees': {
                'upsell': 0,
                'confirmation': 0,
                'cancellation': 0,
                'fulfillment': 0,
                'shipping': 0,
                'return': 0,
                'warehouse': 0,
            }
        })

@login_required
def generate_invoice(request, order_id):
    """Generate invoice HTML for an order."""
    order = get_object_or_404(Order, id=order_id)
    
    try:
        # Get payment information
        payment = OrderPayment.objects.filter(order=order).first()
        
        # Get fees
        try:
            fees = OrderFees.objects.get(order=order)
            total_fees = fees.get_total_fees()
        except OrderFees.DoesNotExist:
            fees = None
            total_fees = 0
        
        # Prepare context for invoice template
        context = {
            'order': order,
            'payment': payment,
            'fees': fees,
            'total_fees': total_fees,
            'grand_total': order.get_total_price() + total_fees,
        }
        
        # Render invoice HTML
        invoice_html = render_to_string('finance/invoice_template.html', context)
        
        return JsonResponse({
            'success': True,
            'invoice_html': invoice_html,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def dashboard(request):
    """Finance dashboard with summary statistics."""
    # Get summary statistics using F expressions to calculate total price in the database
    total_revenue = OrderPayment.objects.filter(payment_status='paid').aggregate(
        total=Sum('amount')  # Use the amount field directly from the payment table
    )['total'] or 0
    
    paid_orders_count = OrderPayment.objects.filter(payment_status='paid').count()
    pending_orders_count = OrderPayment.objects.filter(payment_status='pending').count()
    
    # Get recent payments
    recent_payments = OrderPayment.objects.select_related(
        'order', 'order__seller'
    ).order_by('-payment_date')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'paid_orders_count': paid_orders_count,
        'pending_orders_count': pending_orders_count,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'finance/dashboard.html', context)

@login_required
def create_invoice(request):
    """Create a new invoice."""
    if request.method == 'POST':
        # Handle invoice creation
        order_id = request.POST.get('order_id')
        
        if not order_id:
            messages.error(request, _('Order ID is required.'))
            return redirect('finance:create_invoice')
            
        try:
            order = Order.objects.get(id=order_id)
            
            # Logic to create invoice would go here
            # For now, just redirect to view the invoice
            
            messages.success(request, _('Invoice created successfully.'))
            return redirect('finance:finance_list')
            
        except Order.DoesNotExist:
            messages.error(request, _('Order not found.'))
            return redirect('finance:create_invoice')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('finance:create_invoice')
    
    # Get all orders that don't have an invoice yet
    orders = Order.objects.select_related('seller').all()
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'finance/create_invoice.html', context)

@login_required
def financial_reports(request):
    """View financial reports and analytics."""
    # Get date range from request or use default (current month)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('type', 'all')  # Default to 'all' if not specified
    
    # Get payment data for charts
    payments = OrderPayment.objects.all()
    
    # Apply date filters if provided
    if start_date and end_date:
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    # Calculate summary statistics
    total_revenue = payments.filter(payment_status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending = payments.filter(payment_status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get fees data for expenses
    fees = OrderFees.objects.all()
    if start_date and end_date:
        fees = fees.filter(order__date__range=[start_date, end_date])
    
    # Calculate total expenses
    total_expenses = fees.aggregate(
        total=Sum(F('upsell_fees') + F('confirmation_fees') + F('cancellation_fees') + 
                  F('fulfillment_fees') + F('shipping_fees') + F('return_fees') + F('warehouse_fees'))
    )['total'] or 0
    
    # Calculate net profit
    net_profit = total_revenue - total_expenses
    
    # Get payment methods breakdown
    payment_methods = payments.filter(payment_status='paid').values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Set appropriate title and focus based on report type
    title = _("Financial Reports")
    focus_section = None
    
    if report_type == 'revenue':
        title = _("Revenue Report")
        focus_section = 'revenue'
    elif report_type == 'expenses':
        title = _("Expenses Report")
        focus_section = 'expenses'
    elif report_type == 'profit':
        title = _("Profit Analysis")
        focus_section = 'profit'
    
    context = {
        'title': title,
        'focus_section': focus_section,
        'report_type': report_type,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'total_pending': total_pending,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'finance/financial_reports.html', context)

@login_required
def pending_payments(request):
    """Manage pending payments."""
    # Get all pending payments
    pending_payments = OrderPayment.objects.filter(
        payment_status='pending'
    ).select_related('order', 'order__seller')
    
    if request.method == 'POST':
        # Handle payment updates
        payment_ids = request.POST.getlist('payment_ids')
        action = request.POST.get('action')
        
        if not payment_ids:
            messages.error(request, _('No payments selected.'))
            return redirect('finance:pending_payments')
            
        try:
            if action == 'mark_paid':
                # Update selected payments to paid
                OrderPayment.objects.filter(id__in=payment_ids).update(payment_status='paid')
                messages.success(request, _('Payments marked as paid successfully.'))
            elif action == 'mark_postponed':
                # Update selected payments to postponed
                OrderPayment.objects.filter(id__in=payment_ids).update(payment_status='postponed')
                messages.success(request, _('Payments marked as postponed successfully.'))
            else:
                messages.error(request, _('Invalid action.'))
                
            return redirect('finance:pending_payments')
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('finance:pending_payments')
    
    context = {
        'pending_payments': pending_payments,
    }
    
    return render(request, 'finance/pending_payments.html', context)

@login_required
def finance_settings(request):
    """Configure finance options."""
    if request.method == 'POST':
        # Handle settings updates
        # Example: Update default fees, payment methods, etc.
        try:
            # Sample implementation - would be expanded based on actual settings
            messages.success(request, _('Finance settings updated successfully.'))
            return redirect('finance:finance_settings')
        except Exception as e:
            messages.error(request, str(e))
    
    # Prepare context with current settings
    context = {
        'payment_methods': OrderPayment.PAYMENT_METHODS,
        'payment_statuses': OrderPayment.PAYMENT_STATUS,
    }
    
    return render(request, 'finance/finance_settings.html', context) 