from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from orders.models import Order, OrderItem
from sellers.models import Product, Seller
from inventory.models import Warehouse, InventoryRecord
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample orders and products for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create warehouses
        warehouses = []
        warehouse_names = ['Main Warehouse', 'Secondary Warehouse', 'Regional Warehouse']
        for name in warehouse_names:
            warehouse, created = Warehouse.objects.get_or_create(
                name=name,
                defaults={
                    'location': f'{name} Location',
                    'description': f'This is the {name}',
                    'is_active': True
                }
            )
            warehouses.append(warehouse)
            if created:
                self.stdout.write(f'Created warehouse: {name}')
        
        # Get users with Seller role and create Seller instances
        try:
            from roles.models import UserRole
            seller_users = User.objects.filter(
                user_roles__role__name='Seller',
                user_roles__is_active=True
            ).distinct()
        except ImportError:
            seller_users = User.objects.filter(is_active=True)
        
        if not seller_users.exists():
            self.stdout.write('No seller users found. Creating a sample seller...')
            seller_user = User.objects.create(
                email='sample_seller@example.com',
                full_name='Sample Seller',
                phone_number='+1234567890',
                is_active=True
            )
            seller_users = [seller_user]
        
        # Create Seller instances for users
        seller_instances = []
        for user in seller_users:
            seller_instance, created = Seller.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.full_name,
                    'phone': user.phone_number,
                    'email': user.email,
                }
            )
            seller_instances.append(seller_instance)
            if created:
                self.stdout.write(f'Created seller instance for: {user.email}')
        
        # Create sample products
        products = []
        product_data = [
            {
                'name_en': 'Smartphone X1',
                'name_ar': 'هاتف ذكي X1',
                'code': 'PHONE001',
                'description': 'Latest smartphone with advanced features',
                'selling_price': Decimal('599.99'),
                'purchase_price': Decimal('450.00'),
            },
            {
                'name_en': 'Laptop Pro',
                'name_ar': 'لابتوب برو',
                'code': 'LAPTOP001',
                'description': 'Professional laptop for work and gaming',
                'selling_price': Decimal('1299.99'),
                'purchase_price': Decimal('950.00'),
            },
            {
                'name_en': 'Wireless Headphones',
                'name_ar': 'سماعات لاسلكية',
                'code': 'HEAD001',
                'description': 'High-quality wireless headphones',
                'selling_price': Decimal('199.99'),
                'purchase_price': Decimal('120.00'),
            },
            {
                'name_en': 'Smart Watch',
                'name_ar': 'ساعة ذكية',
                'code': 'WATCH001',
                'description': 'Fitness and health tracking smartwatch',
                'selling_price': Decimal('299.99'),
                'purchase_price': Decimal('180.00'),
            },
            {
                'name_en': 'Tablet Air',
                'name_ar': 'تابلت إير',
                'code': 'TABLET001',
                'description': 'Lightweight tablet for productivity',
                'selling_price': Decimal('449.99'),
                'purchase_price': Decimal('320.00'),
            },
        ]
        
        for product_info in product_data:
            seller_instance = random.choice(seller_instances)
            product, created = Product.objects.get_or_create(
                code=product_info['code'],
                defaults={
                    **product_info,
                    'seller': seller_instance.user
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name_en}')
        
        # Create sample orders
        order_statuses = ['pending', 'confirmed', 'in_delivery', 'delivered']
        customer_names = ['Ahmed Al Mansouri', 'Fatima Al Zahra', 'Omar Al Rashid', 'Khalid Al Qasimi', 'Aisha Al Farsi']
        
        for i in range(15):  # Create 15 sample orders
            # Create order
            seller_instance = random.choice(seller_instances)
            customer_name = random.choice(customer_names)
            order = Order.objects.create(
                customer_phone=f"+9715{random.randint(10000000, 99999999)}",
                seller=seller_instance,
                status=random.choice(order_statuses),
                date=timezone.now() - timezone.timedelta(days=random.randint(0, 30))
            )
            
            # Add order items
            order_items = random.sample(products, random.randint(1, 3))
            
            for product in order_items:
                quantity = random.randint(1, 5)
                price_per_unit = product.selling_price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price_per_unit
                )
            
            self.stdout.write(f'Created order: {order.order_code} - {order.customer_phone}')
        
        # Create inventory records for products
        for product in products:
            for warehouse in warehouses:
                quantity = random.randint(0, 100)
                if quantity > 0:
                    InventoryRecord.objects.get_or_create(
                        product=product,
                        warehouse=warehouse,
                        defaults={'quantity': quantity}
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        ) 