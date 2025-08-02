# stock_keeper/management/commands/setup_stock_keeper_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from stock_keeper.models import Warehouse, WarehouseInventory, InventoryMovement, StockAlert
from sellers.models import Product
from orders.models import Order
from users.models import User
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Set up sample stock keeper data with warehouses and inventory'

    def handle(self, *args, **options):
        self.stdout.write('Setting up stock keeper data...')
        
        # Create stock keeper group if it doesn't exist
        stock_keeper_group, created = Group.objects.get_or_create(name='Stock Keepers')
        if created:
            self.stdout.write('Created Stock Keepers group')
        
        # Create sample warehouses
        warehouses_data = [
            {
                'name': 'Dubai Main Warehouse',
                'country': 'UAE',
                'zone': 'Dubai',
                'address': 'Sheikh Zayed Road, Dubai, UAE',
                'contact_person': 'Ahmed Khalil',
                'contact_phone': '+971-50-123-4567',
                'contact_email': 'ahmed.khalil@atlas.com',
                'is_active': True,
            },
            {
                'name': 'Abu Dhabi Branch',
                'country': 'UAE',
                'zone': 'Abu Dhabi',
                'address': 'Corniche Road, Abu Dhabi, UAE',
                'contact_person': 'Fatima Al Mansouri',
                'contact_phone': '+971-50-987-6543',
                'contact_email': 'fatima.mansouri@atlas.com',
                'is_active': True,
            },
            {
                'name': 'Sharjah Distribution Center',
                'country': 'UAE',
                'zone': 'Sharjah',
                'address': 'Industrial Area 18, Sharjah, UAE',
                'contact_person': 'Omar Hassan',
                'contact_phone': '+971-50-555-1234',
                'contact_email': 'omar.hassan@atlas.com',
                'is_active': True,
            },
        ]
        
        warehouses = []
        for warehouse_data in warehouses_data:
            warehouse, created = Warehouse.objects.get_or_create(
                name=warehouse_data['name'],
                defaults=warehouse_data
            )
            warehouses.append(warehouse)
            if created:
                self.stdout.write(f'Created warehouse: {warehouse.name}')
        
        # Get existing products or create some if needed
        products = Product.objects.all()  # Remove is_active filter as it doesn't exist
        if not products.exists():
            self.stdout.write('No products found. Please create products first.')
            return
        
        # Create sample inventory for each warehouse
        for warehouse in warehouses:
            self.stdout.write(f'Setting up inventory for {warehouse.name}...')
            
            for product in products[:10]:  # Use first 10 products
                # Create inventory with random quantities
                quantity = random.randint(0, 50)
                min_stock = random.randint(5, 15)
                max_stock = random.randint(50, 100)
                location_codes = ['A-01', 'A-02', 'B-01', 'B-02', 'C-01', 'C-02', 'D-01', 'D-02']
                
                inventory, created = WarehouseInventory.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': quantity,
                        'location_code': random.choice(location_codes),
                        'min_stock_level': min_stock,
                        'max_stock_level': max_stock,
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Added {product.name_en}: {quantity} units')
        
        # Create sample inventory movements
        movement_types = ['stock_in', 'stock_out', 'transfer']
        reasons = ['Supplier delivery', 'Customer order', 'Inter-warehouse transfer', 'Stock adjustment']
        
        for i in range(20):
            product = random.choice(list(products))
            warehouse = random.choice(warehouses)
            movement_type = random.choice(movement_types)
            quantity = random.randint(1, 10)
            
            # Create movement record
            movement = InventoryMovement.objects.create(
                movement_type=movement_type,
                product=product,
                quantity=quantity,
                from_warehouse=warehouse if movement_type in ['stock_out', 'transfer'] else None,
                to_warehouse=warehouse if movement_type in ['stock_in', 'transfer'] else None,
                created_by=User.objects.first(),
                processed_by=User.objects.first(),
                status='completed' if random.choice([True, False]) else 'pending',
                reason=random.choice(reasons),
                notes=f'Sample movement {i+1}',
                condition='good',
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            if movement.status == 'pending':
                self.stdout.write(f'Created pending movement: {movement.movement_type} {product.name_en}')
        
        # Create sample stock alerts
        alert_types = ['low_stock', 'out_of_stock', 'overstocked']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        for i in range(10):
            product = random.choice(list(products))
            warehouse = random.choice(warehouses)
            alert_type = random.choice(alert_types)
            priority = random.choice(priorities)
            
            alert = StockAlert.objects.create(
                alert_type=alert_type,
                priority=priority,
                product=product,
                warehouse=warehouse,
                message=f'Sample alert for {product.name_en} in {warehouse.name}',
                is_resolved=random.choice([True, False]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 7))
            )
            
            if not alert.is_resolved:
                self.stdout.write(f'Created active alert: {alert_type} for {product.name_en}')
        
        # Create sample orders for shipping
        order_statuses = ['processing', 'pending', 'confirmed']
        priorities = ['low', 'medium', 'high']
        
        for i in range(15):
            product = random.choice(list(products))
            status = random.choice(order_statuses)
            priority = random.choice(priorities)
            quantity = random.randint(1, 5)
            
            order = Order.objects.create(
                order_code=f'ORD-{10000 + i}',
                product=product,
                quantity=quantity,
                status=status,
                created_at=timezone.now() - timedelta(days=random.randint(1, 14))
            )
            
            if status == 'processing':
                self.stdout.write(f'Created ready order: {order.order_code} for {product.name_en}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up stock keeper data:\n'
                f'- {len(warehouses)} warehouses\n'
                f'- {products.count()} products with inventory\n'
                f'- {InventoryMovement.objects.count()} movements\n'
                f'- {StockAlert.objects.count()} alerts\n'
                f'- {Order.objects.count()} orders'
            )
        ) 