from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from sellers.models import Product
from orders.models import Order, OrderItem
from sourcing.models import SourcingRequest, Supplier

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup sample seller data with products, orders, and sourcing requests'

    def handle(self, *args, **options):
        self.stdout.write('Setting up seller data...')
        
        # Create sample seller
        seller, created = User.objects.get_or_create(
            email='seller@atlasfulfillment.ae',
            defaults={
                'full_name': 'Ahmed Al-Rashid',
                'phone_number': '+971-50-123-4567',
                'is_active': True
            }
        )
        
        if created:
            # Assign Seller role
            from roles.models import Role, UserRole
            seller_role = Role.objects.filter(name='Seller').first()
            if seller_role:
                UserRole.objects.create(
                    user=seller,
                    role=seller_role,
                    is_primary=True,
                    is_active=True
                )
            self.stdout.write(f'Created seller: {seller.full_name}')
        else:
            self.stdout.write(f'Seller already exists: {seller.full_name}')
        
        # Create sample products
        products_data = [
            {
                'name_en': 'Smartphone X1',
                'name_ar': 'هاتف ذكي إكس 1',
                'code': 'SPX1-001',
                'description': 'Latest smartphone with advanced features',
                'selling_price': Decimal('1299.99'),
                'purchase_price': Decimal('899.99'),
                'seller': seller
            },
            {
                'name_en': 'Laptop Pro',
                'name_ar': 'لابتوب برو',
                'code': 'LAP-002',
                'description': 'Professional laptop for work and gaming',
                'selling_price': Decimal('2499.99'),
                'purchase_price': Decimal('1799.99'),
                'seller': seller
            },
            {
                'name_en': 'Wireless Headphones',
                'name_ar': 'سماعات لاسلكية',
                'code': 'WH-003',
                'description': 'High-quality wireless headphones',
                'selling_price': Decimal('299.99'),
                'purchase_price': Decimal('199.99'),
                'seller': seller
            },
            {
                'name_en': 'Gaming Mouse',
                'name_ar': 'فأرة ألعاب',
                'code': 'GM-004',
                'description': 'Precision gaming mouse with RGB',
                'selling_price': Decimal('149.99'),
                'purchase_price': Decimal('89.99'),
                'seller': seller
            },
            {
                'name_en': 'Mechanical Keyboard',
                'name_ar': 'لوحة مفاتيح ميكانيكية',
                'code': 'MK-005',
                'description': 'Premium mechanical keyboard',
                'selling_price': Decimal('399.99'),
                'purchase_price': Decimal('249.99'),
                'seller': seller
            }
        ]
        
        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                code=product_data['code'],
                defaults=product_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name_en}')
        
        # Create sample orders
        customers = ['Ahmed Al-Rashid', 'Fatima Hassan', 'Omar Al-Zahra', 'Layla Al-Amiri', 'Mohamed Abbas']
        statuses = ['pending', 'pending_confirmation', 'confirmed', 'cancelled']
        
        for i in range(20):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            price_per_unit = product.selling_price
            
            order = Order.objects.create(
                customer=random.choice(customers),
                date=timezone.now() - timedelta(days=random.randint(1, 30)),
                product=product,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=random.choice(statuses),
                shipping_address=f'Address {i+1}',
                city='Dubai',
                state='Dubai',
                zip_code='12345',
                country='UAE',
                notes=f'Sample order {i+1}'
            )
            
            self.stdout.write(f'Created order: {order.order_code} - {order.customer}')
        
        # Create sample suppliers
        suppliers_data = [
            {'name': 'TechSupplies Co.', 'country': 'China'},
            {'name': 'Electronics Plus', 'country': 'South Korea'},
            {'name': 'Gaming Gear Ltd.', 'country': 'Taiwan'},
            {'name': 'Audio Solutions', 'country': 'Germany'},
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults={
                    'country': supplier_data['country'],
                    'contact_person': f'Contact {supplier_data["name"]}',
                    'email': f'contact@{supplier_data["name"].lower().replace(" ", "").replace(".", "").replace(",", "")}.com',
                    'phone': f'+86{random.randint(100000000, 999999999)}',
                    'quality_score': Decimal(str(random.uniform(3.5, 5.0))),
                    'delivery_score': Decimal(str(random.uniform(3.5, 5.0))),
                    'price_score': Decimal(str(random.uniform(3.5, 5.0))),
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')
        
        # Create sample sourcing requests
        sourcing_statuses = ['draft', 'submitted', 'approved', 'in_progress']
        
        for i in range(8):
            supplier = random.choice(suppliers)
            product = random.choice(products)
            
            sourcing_request = SourcingRequest.objects.create(
                seller=seller,
                supplier=supplier,
                product=product,
                product_name=product.name_en,
                carton_quantity=random.randint(10, 50),
                unit_quantity=random.randint(10, 100),
                total_units=random.randint(100, 5000),
                source_country=supplier.country,
                destination_country='UAE',
                finance_source='self_financed',
                cost_per_unit=product.purchase_price * Decimal('0.7'),  # 30% discount
                total_cost=product.purchase_price * Decimal('0.7') * random.randint(100, 5000),
                shipping_cost=Decimal(str(random.uniform(100, 500))),
                customs_fees=Decimal(str(random.uniform(50, 200))),
                grand_total=Decimal(str(random.uniform(1000, 5000))),
                weight=Decimal(str(random.uniform(10, 100))),
                status=random.choice(sourcing_statuses),
                priority=random.choice(['low', 'medium', 'high']),
                notes=f'Sample sourcing request {i+1}'
            )
            
            self.stdout.write(f'Created sourcing request: {sourcing_request.request_number}')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully set up seller data:\n'
                f'- 1 seller created\n'
                f'- {len(products)} products created\n'
                f'- 20 orders created\n'
                f'- {len(suppliers)} suppliers created\n'
                f'- 8 sourcing requests created'
            )
        ) 