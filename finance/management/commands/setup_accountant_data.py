from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from finance.models import Payment
from orders.models import Order
from sellers.models import Product
from users.models import User
from roles.models import Role, UserRole
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up accountant data and create accountant user'

    def handle(self, *args, **options):
        self.stdout.write('Setting up accountant data...')
        
        # Create Accountant role if it doesn't exist
        accountant_role, created = Role.objects.get_or_create(
            name='Accountant',
            defaults={
                'description': 'Financial management and accounting operations',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created Accountant role')
        
        # Create accountant user
        accountant_user, created = User.objects.get_or_create(
            email='accountant@atlasfulfillment.com',
            defaults={
                'full_name': 'Sarah Accountant',
                'phone_number': '+971-50-123-4567',
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created accountant user: {accountant_user.email}')
        
        # Assign Accountant role to user
        user_role, created = UserRole.objects.get_or_create(
            user=accountant_user,
            role=accountant_role,
            defaults={
                'is_primary': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Assigned Accountant role to {accountant_user.email}')
        
        # Create sample payments for accountant dashboard
        if Payment.objects.count() == 0:
            self.stdout.write('Creating sample payments...')
            
            # Get existing orders
            orders = Order.objects.all()[:20]  # Use first 20 orders
            
            if not orders.exists():
                self.stdout.write('No orders found. Creating sample orders first...')
                # Create sample orders if none exist
                products = Product.objects.all()[:5]
                if not products.exists():
                    self.stdout.write('No products found. Please create products first.')
                    return
                
                for i in range(10):
                    product = random.choice(products)
                    order = Order.objects.create(
                        order_code=f'ORD-{10000 + i}',
                        customer=f'Customer {i+1}',
                        seller=accountant_user,
                        product=product,
                        quantity=random.randint(1, 3),
                        price_per_unit=Decimal(random.uniform(100, 1000)),
                        status=random.choice(['pending', 'processing', 'completed']),
                        customer_phone=f'+971-50-{random.randint(1000000, 9999999)}',
                        date=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
                    orders = Order.objects.all()
            
            # Create payments for orders
            payment_methods = ['cash', 'credit_card', 'bank_transfer', 'paypal']
            payment_statuses = ['pending', 'completed', 'failed', 'refunded']
            
            for order in orders:
                # Create 1-3 payments per order
                num_payments = random.randint(1, 3)
                for j in range(num_payments):
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_price / num_payments,
                        payment_method=random.choice(payment_methods),
                        payment_status=random.choice(payment_statuses),
                        transaction_id=f'TXN-{random.randint(100000, 999999)}',
                        payment_date=order.date + timedelta(days=random.randint(0, 5)),
                        notes=f'Payment {j+1} for order {order.order_code}'
                    )
            
            self.stdout.write(f'Created {Payment.objects.count()} sample payments')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Accountant data setup complete!\n'
                f'Accountant user: accountant@atlasfulfillment.com\n'
                f'Password: Use Django admin or create password via shell\n'
                f'Total payments: {Payment.objects.count()}\n'
                f'Total orders: {Order.objects.count()}'
            )
        ) 