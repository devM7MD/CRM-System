from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random
from finance.models import Payment
from orders.models import Order
from users.models import User


class Command(BaseCommand):
    help = 'Create real payment data for the finance system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of payment data',
        )

    def handle(self, *args, **options):
        if not options['force']:
            # Check if payment data already exists
            if Payment.objects.exists():
                self.stdout.write(
                    self.style.WARNING(
                        'Payment data already exists. Use --force to recreate.'
                    )
                )
                return

        self.stdout.write('Creating real payment data...')

        # Get existing orders
        orders = Order.objects.all()
        if not orders.exists():
            self.stdout.write(
                self.style.WARNING('No orders found. Please create orders first.')
            )
            return

        with transaction.atomic():
            # Clear existing data if force is used
            if options['force']:
                Payment.objects.all().delete()
                self.stdout.write('Cleared existing payment data.')

            # Payment data
            payment_methods = ['cash', 'credit_card', 'bank_transfer', 'paypal']
            payment_statuses = ['pending', 'completed', 'failed', 'refunded']
            
            # Customer names for realistic data
            customer_names = [
                'John Smith', 'Sarah Johnson', 'Ahmed Ali', 'James Wilson', 'Lisa Chen',
                'Maria Garcia', 'David Brown', 'Emma Davis', 'Michael Lee', 'Anna Rodriguez',
                'Robert Taylor', 'Jennifer White', 'Christopher Martinez', 'Amanda Thompson',
                'Daniel Anderson', 'Jessica Jackson', 'Matthew Wright', 'Nicole Garcia',
                'Andrew Miller', 'Stephanie Moore', 'Joshua Martin', 'Rebecca Lee',
                'Kevin Johnson', 'Michelle Davis', 'Brian Wilson', 'Ashley Brown',
                'Steven Miller', 'Rachel Garcia', 'Timothy Anderson', 'Lauren Taylor'
            ]

            payments_created = 0

            for i, order in enumerate(orders):
                # Create 1-2 payments per order
                num_payments = random.randint(1, 2)
                
                for j in range(num_payments):
                    # Generate realistic payment amounts
                    if j == 0:  # First payment (usually full amount)
                        amount = float(order.total_price)
                    else:  # Partial payment
                        amount = round(float(order.total_price) * random.uniform(0.3, 0.7), 2)
                    
                    # Generate realistic dates
                    payment_date = order.date + timedelta(days=random.randint(0, 7))
                    
                    # Determine status based on payment date
                    if payment_date < timezone.now() - timedelta(days=1):
                        status = random.choice(['completed', 'completed', 'completed', 'refunded'])
                    else:
                        status = random.choice(['pending', 'completed', 'failed'])
                    
                    # Generate transaction ID
                    transaction_id = f"TXN{random.randint(100000, 999999)}"
                    
                    payment = Payment.objects.create(
                        order=order,
                        amount=amount,
                        payment_method=random.choice(payment_methods),
                        payment_status=status,
                        transaction_id=transaction_id,
                        payment_date=payment_date,
                        notes=f"Payment for order {order.order_code}. {random.choice(['Customer requested invoice.', 'Payment processed successfully.', 'Payment received via bank transfer.', 'Credit card payment authorized.'])}"
                    )
                    
                    payments_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {payments_created} payments.'
                )
            ) 