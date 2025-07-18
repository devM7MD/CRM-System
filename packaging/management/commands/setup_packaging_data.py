# packaging/management/commands/setup_packaging_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from packaging.models import PackagingMaterial, PackagingRecord, PackagingTask, PackagingQualityCheck
from orders.models import Order

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up sample packaging data with materials and realistic packaging records'

    def handle(self, *args, **options):
        self.stdout.write('Setting up packaging data...')
        
        # Create packaging materials
        self.create_packaging_materials()
        
        # Create packaging records for existing orders
        self.create_packaging_records()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up packaging data!')
        )

    def create_packaging_materials(self):
        """Create sample packaging materials."""
        materials_data = [
            {
                'name': 'Small Box (20x15x10cm)',
                'material_type': 'box',
                'description': 'Standard small cardboard box for small items',
                'current_stock': 150,
                'min_stock_level': 20,
                'unit': 'pieces',
                'cost_per_unit': Decimal('2.50'),
                'supplier': 'Cardboard Supplies Co.'
            },
            {
                'name': 'Medium Box (30x25x20cm)',
                'material_type': 'box',
                'description': 'Medium cardboard box for medium-sized items',
                'current_stock': 80,
                'min_stock_level': 15,
                'unit': 'pieces',
                'cost_per_unit': Decimal('4.00'),
                'supplier': 'Cardboard Supplies Co.'
            },
            {
                'name': 'Large Box (40x35x30cm)',
                'material_type': 'box',
                'description': 'Large cardboard box for bulky items',
                'current_stock': 45,
                'min_stock_level': 10,
                'unit': 'pieces',
                'cost_per_unit': Decimal('6.50'),
                'supplier': 'Cardboard Supplies Co.'
            },
            {
                'name': 'Bubble Wrap Roll (100m)',
                'material_type': 'bubble_wrap',
                'description': 'Protective bubble wrap for fragile items',
                'current_stock': 25,
                'min_stock_level': 5,
                'unit': 'rolls',
                'cost_per_unit': Decimal('15.00'),
                'supplier': 'Protective Packaging Ltd.'
            },
            {
                'name': 'Packing Tape (50m)',
                'material_type': 'tape',
                'description': 'Strong packing tape for sealing boxes',
                'current_stock': 60,
                'min_stock_level': 10,
                'unit': 'rolls',
                'cost_per_unit': Decimal('3.50'),
                'supplier': 'Adhesive Solutions'
            },
            {
                'name': 'Padded Envelope (A4)',
                'material_type': 'envelope',
                'description': 'Padded envelope for documents and small items',
                'current_stock': 200,
                'min_stock_level': 30,
                'unit': 'pieces',
                'cost_per_unit': Decimal('1.20'),
                'supplier': 'Envelope World'
            },
            {
                'name': 'Polybag (20x30cm)',
                'material_type': 'polybag',
                'description': 'Clear polybag for clothing and soft items',
                'current_stock': 300,
                'min_stock_level': 50,
                'unit': 'pieces',
                'cost_per_unit': Decimal('0.30'),
                'supplier': 'Plastic Packaging Co.'
            },
            {
                'name': 'Filler Paper',
                'material_type': 'filler',
                'description': 'Kraft paper for filling empty spaces',
                'current_stock': 40,
                'min_stock_level': 8,
                'unit': 'kg',
                'cost_per_unit': Decimal('8.00'),
                'supplier': 'Paper Products Inc.'
            },
            {
                'name': 'Shipping Labels (100 per sheet)',
                'material_type': 'label',
                'description': 'Professional shipping labels',
                'current_stock': 15,
                'min_stock_level': 3,
                'unit': 'sheets',
                'cost_per_unit': Decimal('12.00'),
                'supplier': 'Label Solutions'
            },
            {
                'name': 'Custom Box (50x40x35cm)',
                'material_type': 'box',
                'description': 'Custom-sized box for special orders',
                'current_stock': 8,
                'min_stock_level': 5,
                'unit': 'pieces',
                'cost_per_unit': Decimal('12.00'),
                'supplier': 'Custom Packaging Ltd.'
            }
        ]
        
        for material_data in materials_data:
            material, created = PackagingMaterial.objects.get_or_create(
                name=material_data['name'],
                defaults=material_data
            )
            if created:
                self.stdout.write(f'Created material: {material.name}')
            else:
                self.stdout.write(f'Material already exists: {material.name}')

    def create_packaging_records(self):
        """Create packaging records for existing orders."""
        # Get processing orders that don't have packaging records
        orders = Order.objects.filter(
            status='processing'
        ).exclude(
            packaging__isnull=False
        )[:20]  # Limit to 20 orders
        
        if not orders:
            self.stdout.write('No processing orders found for packaging records.')
            return
        
        # Get users for packagers
        users = User.objects.filter(is_active=True)[:5]
        if not users:
            self.stdout.write('No active users found for packagers.')
            return
        
        package_types = ['box', 'envelope', 'polybag', 'tube']
        statuses = ['pending', 'in_progress', 'completed']
        
        for order in orders:
            # Randomly decide if this order should have packaging
            if random.choice([True, False]):
                packager = random.choice(users)
                package_type = random.choice(package_types)
                status = random.choice(statuses)
                
                # Create packaging record
                packaging_record = PackagingRecord.objects.create(
                    order=order,
                    packager=packager,
                    package_type=package_type,
                    package_weight=Decimal(str(random.uniform(0.5, 5.0))),
                    dimensions=f"{random.randint(15, 50)}x{random.randint(10, 40)}x{random.randint(5, 30)}cm",
                    status=status,
                    packaging_notes=f"Sample packaging record for order {order.order_code}"
                )
                
                # Set completion time if completed
                if status == 'completed':
                    packaging_record.packaging_completed = timezone.now() - timedelta(
                        hours=random.randint(1, 24)
                    )
                    packaging_record.save()
                
                # Create packaging task
                task = PackagingTask.objects.create(
                    order=order,
                    assigned_to=packager,
                    priority=random.choice(['low', 'normal', 'high']),
                    status=status,
                    estimated_duration=random.randint(10, 30),
                    notes=f"Packaging task for order {order.order_code}"
                )
                
                # Set task timing
                if status == 'in_progress':
                    task.started_at = timezone.now() - timedelta(hours=random.randint(1, 4))
                elif status == 'completed':
                    task.started_at = timezone.now() - timedelta(hours=random.randint(2, 6))
                    task.completed_at = timezone.now() - timedelta(hours=random.randint(1, 5))
                    task.actual_duration = random.randint(8, 35)
                
                task.save()
                
                # Create quality check for completed packages
                if status == 'completed' and random.choice([True, False]):
                    PackagingQualityCheck.objects.create(
                        packaging_record=packaging_record,
                        checker=random.choice(users),
                        check_type=random.choice(['visual', 'weight', 'dimensions', 'label']),
                        result=random.choice(['pass', 'pass', 'pass', 'fail']),  # 75% pass rate
                        notes="Sample quality check"
                    )
                    
                    packaging_record.quality_check_passed = True
                    packaging_record.quality_check_by = packager
                    packaging_record.quality_check_date = timezone.now()
                    packaging_record.save()
                
                self.stdout.write(f'Created packaging record for order: {order.order_code}')
        
        self.stdout.write(f'Created packaging records for {orders.count()} orders.') 