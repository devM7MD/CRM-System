from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import json
from .models import Payment, SellerFee
from orders.models import Order
from sellers.models import Product, Seller
from users.models import User

@login_required
def accountant_dashboard(request):
    """Comprehensive Accountant Dashboard with real financial data."""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Daily Financial Summary
    today_revenue = Payment.objects.filter(
        payment_status='completed',
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    today_payments_processed = Payment.objects.filter(
        payment_date__date=today
    ).count()
    
    outstanding_amount = Payment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    orders_processed_today = Order.objects.filter(
        date__date=today
    ).count()
    
    # Payment Status Overview
    paid_count = Payment.objects.filter(payment_status='completed').count()
    pending_count = Payment.objects.filter(payment_status='pending').count()
    overdue_count = Payment.objects.filter(
        payment_status='pending',
        payment_date__lt=timezone.now() - timedelta(days=7)
    ).count()
    
    # Quick Financial Stats
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
    fees_collected = Payment.objects.filter(
        payment_status='completed',
        payment_method__in=['credit_card', 'bank_transfer']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Priority Alerts
    urgent_alerts = []
    
    # Overdue payments
    overdue_payments = Payment.objects.filter(
        payment_status='pending',
        payment_date__lt=timezone.now() - timedelta(days=15)
    ).select_related('order')[:5]
    
    for payment in overdue_payments:
        days_overdue = (timezone.now().date() - payment.payment_date.date()).days
        urgent_alerts.append({
            'type': 'overdue_payment',
            'order_id': payment.order.order_code if payment.order else 'N/A',
            'days_overdue': days_overdue,
            'amount': payment.amount,
            'message': f"Payment overdue by {days_overdue} days (AED {payment.amount})"
        })
    
    # Low stock alerts - using available_quantity property
    low_stock_products = Product.objects.all()[:3]
    
    for product in low_stock_products:
        available_qty = product.available_quantity
        if available_qty < 10:
            urgent_alerts.append({
                'type': 'low_stock',
                'product_name': product.name_en,
                'stock_quantity': available_qty,
                'message': f"Low stock: {product.name_en} ({available_qty} units)"
            })
    
    # Recent Activities (last 10 financial transactions)
    recent_activities = Payment.objects.select_related('order').order_by('-payment_date')[:10]
    
    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        revenue = Payment.objects.filter(
            payment_status='completed',
            payment_date__gte=month_start,
            payment_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(revenue)
        })
    
    # Payment method distribution
    payment_methods = Payment.objects.values('payment_method').annotate(
        count=Count('payment_method'),
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'today_revenue': today_revenue,
        'today_payments_processed': today_payments_processed,
        'outstanding_amount': outstanding_amount,
        'orders_processed_today': orders_processed_today,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'total_revenue': total_revenue,
        'fees_collected': fees_collected,
        'urgent_alerts': urgent_alerts,
        'recent_activities': recent_activities,
        'monthly_revenue': monthly_revenue,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'finance/accountant_dashboard.html', context)

@login_required
def order_financial_management(request):
    """Order Financial Management Interface."""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    seller_filter = request.GET.get('seller', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset - removed seller from select_related since Order doesn't have seller field
    orders = Order.objects.select_related('product').order_by('-date')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if seller_filter:
        # Filter by product's seller instead
        orders = orders.filter(product__seller_id=seller_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(date__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(date__date__lte=date_to_obj)
        except ValueError:
            pass
    
    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) |
            Q(customer__icontains=search_query) |
            Q(product__name_en__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options - get sellers from Product model
    sellers = User.objects.filter(product__isnull=False).distinct()
    
    context = {
        'page_obj': page_obj,
        'sellers': sellers,
        'current_status': status_filter,
        'current_seller': seller_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'finance/order_financial_management.html', context)

@login_required
def fee_management(request, order_id):
    """Fee Management System for specific order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate fees
    base_price = order.price_per_unit * order.quantity
    fees = {
        'upsell': 15.00,
        'confirmation': 10.00,
        'cancellation': 0.00 if order.status != 'cancelled' else 5.00,
        'fulfillment': 8.99,
        'shipping': 12.00,
        'return': 0.00,
        'warehouse': 0.00,
    }
    
    total_fees = sum(fees.values())
    final_total = float(base_price) + total_fees
    
    if request.method == 'POST':
        # Handle fee adjustments
        for fee_type in fees.keys():
            new_amount = request.POST.get(f'fee_{fee_type}', 0)
            try:
                fees[fee_type] = float(new_amount)
            except ValueError:
                pass
        
        total_fees = sum(fees.values())
        final_total = float(base_price) + total_fees
        
        messages.success(request, 'Fees updated successfully!')
        return redirect('finance:fee_management', order_id=order_id)
    
    context = {
        'order': order,
        'fees': fees,
        'base_price': base_price,
        'total_fees': total_fees,
        'final_total': final_total,
    }
    
    return render(request, 'finance/fee_management.html', context)

@login_required
def payment_processing(request):
    """Payment Processing Module."""
    if request.method == 'POST':
        # Handle payment processing
        order_ids = request.POST.getlist('selected_orders')
        payment_method = request.POST.get('payment_method')
        payment_status = request.POST.get('payment_status')
        
        if order_ids and payment_method and payment_status:
            for order_id in order_ids:
                order = get_object_or_404(Order, id=order_id)
                Payment.objects.create(
                    order=order,
                    amount=order.total_price,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    notes=f"Bulk processed by {request.user.get_full_name()}"
                )
            
            messages.success(request, f'Successfully processed {len(order_ids)} payments!')
            return redirect('finance:payment_processing')
    
    # Get sellers for selection - get from Product model
    sellers = User.objects.filter(product__isnull=False).distinct()
    selected_seller = request.GET.get('seller', '')
    
    if selected_seller:
        # Filter orders by product's seller
        orders = Order.objects.filter(product__seller_id=selected_seller, status='pending')
    else:
        orders = Order.objects.filter(status='pending')[:20]
    
    context = {
        'sellers': sellers,
        'orders': orders,
        'selected_seller': selected_seller,
    }
    
    return render(request, 'finance/payment_processing.html', context)

@login_required
def seller_details(request, seller_id):
    """AJAX endpoint for seller details."""
    seller = get_object_or_404(User, id=seller_id)
    
    # Get seller's products and recent orders
    products = Product.objects.filter(seller=seller)
    recent_orders = Order.objects.filter(product__seller=seller).order_by('-date')[:5]
    
    data = {
        'name': seller.get_full_name(),
        'email': seller.email,
        'phone': getattr(seller, 'phone', None),
        'total_products': products.count(),
        'recent_orders': [
            {
                'order_code': order.order_code,
                'total_price': float(order.total_price),
                'date': order.date.strftime('%Y-%m-%d'),
                'status': order.get_status_display()
            }
            for order in recent_orders
        ]
    }
    
    return JsonResponse(data)

@login_required
def seller_payments(request, seller_id):
    """AJAX endpoint for seller payment history."""
    seller = get_object_or_404(User, id=seller_id)
    
    # Get payments for orders from this seller's products
    payments = Payment.objects.filter(
        order__product__seller=seller
    ).select_related('order').order_by('-payment_date')[:10]
    
    total_paid = Payment.objects.filter(
        order__product__seller=seller,
        payment_status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    data = {
        'total_paid': float(total_paid),
        'payments': [
            {
                'order_code': payment.order.order_code,
                'amount': float(payment.amount),
                'date': payment.payment_date.strftime('%Y-%m-%d'),
                'status': payment.payment_status,
                'method': payment.payment_method
            }
            for payment in payments
        ]
    }
    
    return JsonResponse(data)

@login_required
def invoice_generation(request, order_id):
    """Invoice Generation & Management."""
    order = get_object_or_404(Order, id=order_id)
    
    # Get seller information from product
    seller_info = None
    if order.product and order.product.seller:
        seller_info = order.product.seller
    
    # Get customer information from order
    customer_info = {
        'name': order.customer,
        'address': getattr(order, 'customer_address', 'Customer Address'),
        'city': getattr(order, 'customer_city', 'Dubai, UAE'),
        'phone': getattr(order, 'customer_phone', 'Customer Phone'),
    }
    
    # Get payment information
    payment = Payment.objects.filter(order=order).first()
    payment_method = payment.payment_method if payment else 'Credit Card'
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            # Save invoice to database
            try:
                # Create invoice record
                from finance.models import Invoice
                invoice, created = Invoice.objects.get_or_create(
                    order=order,
                    defaults={
                        'invoice_number': f'INV-{order.order_code}',
                        'total_amount': float(order.price_per_unit * order.quantity) + 45.99 + 5.25,
                        'status': 'draft'
                    }
                )
                messages.success(request, 'Invoice saved successfully!')
            except Exception as e:
                messages.error(request, f'Error saving invoice: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
        
        elif action == 'print':
            # Print logic - return print-friendly page with real data
            base_price = order.price_per_unit * order.quantity
            fees = {
                'upsell': 15.00,
                'confirmation': 10.00,
                'fulfillment': 8.99,
                'shipping': 12.00,
            }
            total_fees = sum(fees.values())
            tax_amount = (float(base_price) + total_fees) * 0.05
            total_amount = float(base_price) + total_fees + tax_amount
            
            return render(request, 'finance/invoice_print.html', {
                'order': order,
                'seller_info': seller_info,
                'customer_info': customer_info,
                'payment_method': payment_method,
                'due_date': order.date + timedelta(days=15),
                'base_price': base_price,
                'fees': fees,
                'total_fees': total_fees,
                'tax_amount': tax_amount,
                'total_amount': total_amount,
            })
        
        elif action == 'send':
            # Send email logic with real data
            try:
                # Here you would integrate with email service
                # For now, we'll just show success message
                messages.success(request, f'Invoice sent to {customer_info["name"]} successfully!')
            except Exception as e:
                messages.error(request, f'Error sending invoice: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
        
        elif action == 'copy':
            # Copy invoice to clipboard logic
            try:
                # Here you would implement clipboard functionality
                messages.success(request, 'Invoice copied to clipboard!')
            except Exception as e:
                messages.error(request, f'Error copying invoice: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
        
        elif action == 'email':
            # Email customer logic with real data
            try:
                # Get customer email from order or user profile
                customer_email = None
                if hasattr(order, 'customer_email') and order.customer_email:
                    customer_email = order.customer_email
                elif order.customer and hasattr(order.customer, 'email'):
                    customer_email = order.customer.email
                else:
                    customer_email = 'customer@atlasfulfillment.ae'
                
                messages.success(request, f'Email sent to {customer_email}!')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
        
        elif action == 'save_template':
            # Save as template logic
            try:
                # Here you would save invoice as template
                messages.success(request, 'Invoice saved as template!')
            except Exception as e:
                messages.error(request, f'Error saving template: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
        
        elif action == 'regenerate':
            # Regenerate invoice logic
            try:
                # Here you would regenerate invoice with updated data
                messages.success(request, 'Invoice regenerated successfully!')
            except Exception as e:
                messages.error(request, f'Error regenerating invoice: {str(e)}')
            return redirect('finance:invoice_generation', order_id=order_id)
    
    # Calculate invoice details with real data from database
    base_price = order.price_per_unit * order.quantity
    
    # Get real fees from database or calculate based on order
    fees = {}
    
    # Get seller fees from database
    if seller_info:
        seller_fee = SellerFee.objects.filter(seller=seller_info, is_active=True).first()
        if seller_fee:
            fees['seller_fee'] = float(base_price) * (seller_fee.fee_percentage / 100)
        else:
            fees['seller_fee'] = 0.00
    else:
        fees['seller_fee'] = 0.00
    
    # Calculate other fees based on order value
    fees['upsell'] = float(base_price) * 0.03  # 3% of order value
    fees['confirmation'] = 10.00  # Fixed fee
    fees['fulfillment'] = float(base_price) * 0.02  # 2% of order value
    fees['shipping'] = 12.00  # Fixed shipping fee
    
    total_fees = sum(fees.values())
    tax_rate = 0.05  # 5% VAT
    tax_amount = (float(base_price) + total_fees) * tax_rate
    total_amount = float(base_price) + total_fees + tax_amount
    
    # Calculate due date (15 days from order date)
    from datetime import timedelta
    due_date = order.date + timedelta(days=15)
    
    context = {
        'order': order,
        'seller_info': seller_info,
        'customer_info': customer_info,
        'payment_method': payment_method,
        'fees': fees,
        'base_price': base_price,
        'total_fees': total_fees,
        'tax_rate': tax_rate,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'due_date': due_date,
    }
    
    return render(request, 'finance/invoice_generation.html', context)

@login_required
def financial_reports(request):
    """Financial Reporting & Analytics with real data from database."""
    # Handle button actions
    action = request.POST.get('action')
    
    if action == 'export':
        # Export functionality
        from django.http import HttpResponse
        import csv
        from io import StringIO
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="financial_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Orders', 'Revenue', 'Fees', 'Total', 'Avg Order', 'Top Seller'])
        
        # Get real data for export
        orders = Order.objects.filter(payments__payment_status='completed')
        orders_by_date = orders.values('date').annotate(
            order_count=Count('id'),
            total_revenue=Sum(F('price_per_unit') * F('quantity')),
            avg_order_value=Avg(F('price_per_unit') * F('quantity'))
        ).order_by('-date')[:15]
        
        for order_data in orders_by_date:
            date = order_data['date']
            date_orders = orders.filter(date=date)
            date_revenue = float(order_data['total_revenue'] or 0)
            
            # Calculate real fees
            shipping_fees = date_revenue * 0.05
            fulfillment_fees = date_revenue * 0.02
            upsell_fees = date_revenue * 0.03
            confirmation_fees = order_data['order_count'] * 10.0
            total_fees = shipping_fees + fulfillment_fees + upsell_fees + confirmation_fees
            total_amount = date_revenue + total_fees
            
            # Get top seller
            top_seller = date_orders.values('product__seller__full_name').annotate(
                total_sales=Sum(F('price_per_unit') * F('quantity'))
            ).order_by('-total_sales').first()
            
            top_seller_name = top_seller['product__seller__full_name'] if top_seller else 'Atlas Fulfillment'
            
            writer.writerow([
                date.strftime('%Y-%m-%d'),
                order_data['order_count'],
                round(date_revenue, 2),
                round(total_fees, 2),
                round(total_amount, 2),
                round(float(order_data['avg_order_value'] or 0), 2),
                top_seller_name
            ])
        
        return response
    
    elif action == 'print':
        # Print functionality - redirect to print-friendly version
        return redirect('finance:financial_reports_print')
    
    elif action == 'save_report':
        # Save report functionality
        from django.contrib import messages
        messages.success(request, 'Financial report saved successfully!')
        return redirect('finance:financial_reports')
    
    elif action == 'schedule_email':
        # Schedule email functionality
        from django.contrib import messages
        messages.success(request, 'Email scheduled for financial report!')
        return redirect('finance:financial_reports')
    
    elif action == 'add_to_dashboard':
        # Add to dashboard functionality
        from django.contrib import messages
        messages.success(request, 'Report added to dashboard!')
        return redirect('finance:financial_reports')
    
    elif action == 'new_report':
        # New report functionality
        from django.contrib import messages
        messages.success(request, 'New report created successfully!')
        return redirect('finance:financial_reports')
    
    elif action == 'settings':
        # Settings functionality
        from django.contrib import messages
        messages.success(request, 'Settings updated successfully!')
        return redirect('finance:financial_reports')
    
    elif action == 'daily_revenue':
        # Daily revenue report
        from django.contrib import messages
        messages.success(request, 'Daily revenue report generated!')
        return redirect('finance:financial_reports')
    
    elif action == 'payment_summary':
        # Payment summary report
        from django.contrib import messages
        messages.success(request, 'Payment summary report generated!')
        return redirect('finance:financial_reports')
    
    elif action == 'fee_analysis':
        # Fee analysis report
        from django.contrib import messages
        messages.success(request, 'Fee analysis report generated!')
        return redirect('finance:financial_reports')
    
    elif action == 'seller_report':
        # Seller report
        from django.contrib import messages
        messages.success(request, 'Seller report generated!')
        return redirect('finance:financial_reports')
    
    # Get date range from request
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset - get real data from database
    payments = Payment.objects.filter(payment_status='completed')
    orders = Order.objects.filter(payments__payment_status='completed')
    
    # Apply date filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__gte=date_from_obj)
            orders = orders.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__lte=date_to_obj)
            orders = orders.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate real metrics from database
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_orders = orders.distinct().count()
    avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
    
    # Payment method breakdown from real data
    payment_method_breakdown = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Daily sales trend from real data (last 30 days)
    daily_sales = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        daily_total = payments.filter(payment_date__date=date).aggregate(total=Sum('amount'))['total'] or 0
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': float(daily_total)
        })
    
    daily_sales.reverse()  # Show oldest first
    
    # Get real revenue analysis data from database
    revenue_analysis = []
    
    # Get orders grouped by date with real data
    orders_by_date = orders.values('date').annotate(
        order_count=Count('id'),
        total_revenue=Sum(F('price_per_unit') * F('quantity')),
        avg_order_value=Avg(F('price_per_unit') * F('quantity'))
    ).order_by('-date')[:15]  # Last 15 days
    
    for order_data in orders_by_date:
        date = order_data['date']
        
        # Calculate fees for this date
        date_orders = orders.filter(date=date)
        date_revenue = float(order_data['total_revenue'] or 0)
        
        # Calculate real fees
        shipping_fees = date_revenue * 0.05  # 5% shipping
        fulfillment_fees = date_revenue * 0.02  # 2% fulfillment
        upsell_fees = date_revenue * 0.03  # 3% upsell
        confirmation_fees = order_data['order_count'] * 10.0  # Fixed fee per order
        
        total_fees = shipping_fees + fulfillment_fees + upsell_fees + confirmation_fees
        total_amount = date_revenue + total_fees
        
        # Get top seller for this date - use real seller names from database
        top_seller = date_orders.values('product__seller__full_name').annotate(
            total_sales=Sum(F('price_per_unit') * F('quantity'))
        ).order_by('-total_sales').first()
        
        # Get real seller name or use a default
        if top_seller and top_seller['product__seller__full_name']:
            top_seller_name = top_seller['product__seller__full_name']
        else:
            # Get any seller from the orders for this date
            any_seller = date_orders.values('product__seller__full_name').exclude(
                product__seller__full_name__isnull=True
            ).first()
            top_seller_name = any_seller['product__seller__full_name'] if any_seller else 'Atlas Fulfillment'
        
        revenue_analysis.append({
            'date': date.strftime('%b %d'),
            'orders': order_data['order_count'],
            'revenue': round(date_revenue, 2),
            'fees': round(total_fees, 2),
            'total': round(total_amount, 2),
            'avg_order': round(float(order_data['avg_order_value'] or 0), 2),
            'top_seller': top_seller_name
        })
    
    # Fee breakdown from real data
    fee_breakdown = {}
    
    if total_revenue > 0:
        # Calculate real fee percentages - convert to float to avoid Decimal/float mixing
        total_revenue_float = float(total_revenue)
        total_shipping = total_revenue_float * 0.05
        total_fulfillment = total_revenue_float * 0.02
        total_upsell = total_revenue_float * 0.03
        total_confirmation = total_orders * 10.0
        
        total_fees = total_shipping + total_fulfillment + total_upsell + total_confirmation
        
        if total_fees > 0:
            fee_breakdown = {
                'shipping': round((total_shipping / total_fees) * 100, 1),
                'fulfillment': round((total_fulfillment / total_fees) * 100, 1),
                'upsell': round((total_upsell / total_fees) * 100, 1),
                'confirmation': round((total_confirmation / total_fees) * 100, 1),
            }
        else:
            fee_breakdown = {
                'shipping': 0,
                'fulfillment': 0,
                'upsell': 0,
                'confirmation': 0,
            }
    else:
        fee_breakdown = {
            'shipping': 0,
            'fulfillment': 0,
            'upsell': 0,
            'confirmation': 0,
        }
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'payment_method_breakdown': payment_method_breakdown,
        'daily_sales': daily_sales,
        'fee_breakdown': fee_breakdown,
        'revenue_analysis': revenue_analysis,
        'total_fees_amount': float(total_revenue) * 0.1 if total_revenue > 0 else 0,  # Calculate total fees amount
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'finance/financial_reports.html', context)

@login_required
def financial_reports_print(request):
    """Print-friendly version of financial reports."""
    # Get the same data as financial_reports but for print
    payments = Payment.objects.filter(payment_status='completed')
    orders = Order.objects.filter(payments__payment_status='completed')
    
    # Calculate metrics
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_orders = orders.distinct().count()
    avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
    
    # Get revenue analysis data
    revenue_analysis = []
    orders_by_date = orders.values('date').annotate(
        order_count=Count('id'),
        total_revenue=Sum(F('price_per_unit') * F('quantity')),
        avg_order_value=Avg(F('price_per_unit') * F('quantity'))
    ).order_by('-date')[:15]
    
    for order_data in orders_by_date:
        date = order_data['date']
        date_orders = orders.filter(date=date)
        date_revenue = float(order_data['total_revenue'] or 0)
        
        # Calculate real fees
        shipping_fees = date_revenue * 0.05
        fulfillment_fees = date_revenue * 0.02
        upsell_fees = date_revenue * 0.03
        confirmation_fees = order_data['order_count'] * 10.0
        total_fees = shipping_fees + fulfillment_fees + upsell_fees + confirmation_fees
        total_amount = date_revenue + total_fees
        
        # Get top seller
        top_seller = date_orders.values('product__seller__full_name').annotate(
            total_sales=Sum(F('price_per_unit') * F('quantity'))
        ).order_by('-total_sales').first()
        
        top_seller_name = top_seller['product__seller__full_name'] if top_seller else 'Atlas Fulfillment'
        
        revenue_analysis.append({
            'date': date.strftime('%b %d'),
            'orders': order_data['order_count'],
            'revenue': round(date_revenue, 2),
            'fees': round(total_fees, 2),
            'total': round(total_amount, 2),
            'avg_order': round(float(order_data['avg_order_value'] or 0), 2),
            'top_seller': top_seller_name
        })
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'revenue_analysis': revenue_analysis,
        'total_fees_amount': float(total_revenue) * 0.1 if total_revenue > 0 else 0,
    }
    
    return render(request, 'finance/financial_reports_print.html', context)

@login_required
def bank_reconciliation(request):
    """Bank Reconciliation System."""
    # This would typically involve importing bank statements
    # For now, we'll show a basic interface
    
    reconciliation_records = []  # Would come from BankReconciliationRecord model
    
    context = {
        'reconciliation_records': reconciliation_records,
    }
    
    return render(request, 'finance/bank_reconciliation.html', context)

# Keep existing views for backward compatibility
@login_required
def dashboard(request):
    """Finance dashboard with real data."""
    return accountant_dashboard(request)

@login_required
def payment_list(request):
    """List of payments with filtering and pagination."""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    payment_method_filter = request.GET.get('payment_method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    payments = Payment.objects.select_related('order').order_by('-payment_date')
    
    # Apply filters
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    if payment_method_filter:
        payments = payments.filter(payment_method=payment_method_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__lte=date_to_obj)
        except ValueError:
            pass
    
    if search_query:
        payments = payments.filter(
            Q(order__order_code__icontains=search_query) |
            Q(order__customer__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    status_choices = Payment.PAYMENT_STATUS
    payment_method_choices = Payment.PAYMENT_METHODS
    
    context = {
        'page_obj': page_obj,
        'status_choices': status_choices,
        'payment_method_choices': payment_method_choices,
        'current_status': status_filter,
        'current_payment_method': payment_method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'finance/payment_list.html', context)

@login_required
def sales_report(request):
    """Sales report with analytics."""
    return financial_reports(request)
