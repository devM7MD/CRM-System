from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from finance.models import Payment
from orders.models import Order
from sellers.models import Product
from users.models import User
import random

class Command(BaseCommand):
    help = 'Set up sample finance data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up sample finance data...')
        
        # Create test user
        user, created = User.objects.get_or_create(
            email='test@atlasfulfillment.ae',
            defaults={
                'full_name': 'Test User',
                'phone_number': '+971-50-987-6543',
                'is_active': True
            }
        )
        
        # Create seller user
        seller, created = User.objects.get_or_create(
            email='seller@atlasfulfillment.ae',
            defaults={
                'full_name': 'Ahmed Al-Rashid',
                'phone_number': '+971-50-123-4567',
                'is_active': True
            }
        )
        
        # Create real products
        products = []
        product_names = [
            'iPhone 15 Pro', 'Samsung Galaxy S24', 'MacBook Air M3', 
            'Dell XPS 13', 'Sony WH-1000XM5', 'Apple Watch Series 9',
            'iPad Pro 12.9', 'Samsung Galaxy Tab S9', 'Canon EOS R6',
            'Nike Air Max 270', 'Adidas Ultraboost 22', 'Under Armour HOVR'
        ]
        
        for i, name in enumerate(product_names):
            product, created = Product.objects.get_or_create(
                name_en=name,
                defaults={
                    'name_ar': f'{name} بالعربية',
                    'code': f'PROD-{i+1:03d}',
                    'description': f'Real {name} product with high quality',
                    'selling_price': Decimal(str(random.randint(500, 5000))),
                    'purchase_price': Decimal(str(random.randint(300, 4000))),
                    'seller': seller
                }
            )
            products.append(product)
        
        # Create real orders
        orders = []
        customer_names = [
            'Ahmed Al-Rashid', 'Fatima Hassan', 'Omar Khalil', 'Nadia Mahmoud',
            'Youssef Ibrahim', 'Layla Al-Zahra', 'Khalid Al-Mansouri', 'Aisha Al-Qahtani',
            'Mohammed Al-Sheikh', 'Zainab Al-Hamdan', 'Abdullah Al-Riyadh', 'Mariam Al-Sabah'
        ]
        
        for i in range(20):  # Create 20 real orders
            customer_name = random.choice(customer_names)
            product = random.choice(products)
            quantity = random.randint(1, 5)
            price_per_unit = product.selling_price
            
            order = Order.objects.create(
                order_code=f'ORD-{timezone.now().strftime("%Y%m")}-{i+1:03d}',
                customer=customer_name,
                product=product,
                quantity=quantity,
                price_per_unit=price_per_unit,
                date=timezone.now() - timedelta(days=random.randint(1, 30)),
                status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                notes=f'Real order for {customer_name} - {product.name_en}'
            )
            orders.append(order)
        
        # Create real payments
        payment_methods = ['credit_card', 'bank_transfer', 'cash', 'paypal']
        payment_statuses = ['completed', 'pending', 'failed']
        
        for i, order in enumerate(orders):
            payment_method = random.choice(payment_methods)
            payment_status = random.choice(payment_statuses)
            amount = order.price_per_unit * order.quantity
            
            Payment.objects.create(
                order=order,
                amount=amount,
                payment_method=payment_method,
                payment_status=payment_status,
                transaction_id=f'TXN-{order.order_code}-{i+1}',
                payment_date=order.date + timedelta(days=random.randint(1, 7)),
                notes=f'Real payment for order {order.order_code}'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(products)} products\n'
                f'- {len(orders)} orders\n'
                f'- {Payment.objects.count()} payments\n'
                f'- Test user: {user.username}\n'
                f'- Test seller: {seller.username}'
            )
        ) 