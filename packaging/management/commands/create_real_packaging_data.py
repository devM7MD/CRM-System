from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from packaging.models import PackagingRecord, PackagingMaterial, PackagingTask, PackagingQualityCheck
from orders.models import Order
from datetime import timedelta
import random
import json
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create real packaging data from existing orders and materials'

    def handle(self, *args, **options):
        self.stdout.write('Creating real packaging data...')
        
        # Get existing orders that are processing
        processing_orders = Order.objects.filter(status='processing')
        
        if not processing_orders.exists():
            self.stdout.write(self.style.WARNING('No processing orders found. Creating some first...'))
            # Create some processing orders if none exist
            for i in range(5):
                order = Order.objects.create(
                    order_code=f"ORD-REAL-{i+1:03d}",
                    status='processing',
                    quantity=random.randint(1, 5),
                    price_per_unit=random.uniform(10, 100),
                    customer_phone=f"+1234567890{i}",
                    seller_email=f"seller{i}@example.com"
                )
        
        # Get materials
        materials = list(PackagingMaterial.objects.all())
        if not materials:
            self.stdout.write(self.style.ERROR('No materials found. Please run setup_packaging_data first.'))
            return
        
        # Get users for packagers
        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.ERROR('No active users found.'))
            return
        
        # Create packaging records for processing orders
        processing_orders = Order.objects.filter(status='processing')
        created_count = 0
        
        for order in processing_orders:
            # Skip if already has packaging
            if hasattr(order, 'packaging'):
                continue
                
            packager = random.choice(users)
            
            # Choose random materials
            selected_materials = random.sample(materials, random.randint(1, 3))
            materials_used = {}
            
            for material in selected_materials:
                quantity = random.randint(1, 3)
                materials_used[material.name] = quantity
            
            # Create packaging record
            packaging_record = PackagingRecord.objects.create(
                order=order,
                packager=packager,
                package_type=random.choice(['box', 'envelope', 'polybag']),
                package_weight=random.uniform(0.5, 5.0),
                dimensions=f"{random.randint(15, 50)}x{random.randint(10, 40)}x{random.randint(5, 30)}",
                materials_used=json.dumps(materials_used),
                status=random.choice(['completed', 'in_progress', 'pending']),
                packaging_started=timezone.now() - timedelta(hours=random.randint(1, 24)),
                packaging_completed=timezone.now() - timedelta(hours=random.randint(0, 12)) if random.choice([True, False]) else None,
                packaging_notes=f"Packaged order {order.order_code} with care",
                quality_check_passed=random.choice([True, False]),
                shipping_label_generated=random.choice([True, False]),
                tracking_number=f"TRK-{uuid.uuid4().hex[:12].upper()}"
            )
            
            # Create packaging task
            PackagingTask.objects.create(
                order=order,
                assigned_to=packager,
                priority=random.choice(['low', 'normal', 'high']),
                status=packaging_record.status,
                estimated_duration=random.randint(10, 30),
                actual_duration=random.randint(8, 35) if packaging_record.status == 'completed' else None,
                started_at=packaging_record.packaging_started,
                completed_at=packaging_record.packaging_completed,
                notes=f"Task for order {order.order_code}"
            )
            
            # Create quality checks for completed packages
            if packaging_record.status == 'completed':
                quality_checker = random.choice(users)
                
                # Create multiple quality checks
                check_types = ['visual', 'weight', 'dimensions', 'label', 'seal']
                for check_type in random.sample(check_types, random.randint(2, 4)):
                    check_time = packaging_record.packaging_completed + timedelta(minutes=random.randint(5, 30)) if packaging_record.packaging_completed else timezone.now()
                    PackagingQualityCheck.objects.create(
                        packaging_record=packaging_record,
                        checker=quality_checker,
                        check_type=check_type,
                        result=random.choice(['pass', 'fail', 'conditional']),
                        notes=f"{check_type.title()} check completed for {order.order_code}",
                        checked_at=check_time
                    )
                
                # Update packaging record with quality check info
                packaging_record.quality_check_by = quality_checker
                packaging_record.quality_check_date = packaging_record.packaging_completed + timedelta(minutes=10) if packaging_record.packaging_completed else timezone.now()
                packaging_record.save()
            
            created_count += 1
        
        # Update order status for completed packaging
        completed_packages = PackagingRecord.objects.filter(status='completed')
        for package in completed_packages:
            package.order.status = 'ready_for_shipping'
            package.order.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} packaging records with real data!'
            )
        )
        
        # Show statistics
        total_packages = PackagingRecord.objects.count()
        completed_packages = PackagingRecord.objects.filter(status='completed').count()
        pending_packages = PackagingRecord.objects.filter(status='pending').count()
        in_progress_packages = PackagingRecord.objects.filter(status='in_progress').count()
        
        self.stdout.write(f'Total Packaging Records: {total_packages}')
        self.stdout.write(f'Completed: {completed_packages}')
        self.stdout.write(f'Pending: {pending_packages}')
        self.stdout.write(f'In Progress: {in_progress_packages}')
        
        # Show material usage
        self.stdout.write('\nMaterial Usage:')
        for material in materials:
            usage_count = PackagingRecord.objects.filter(
                materials_used__has_key=material.name
            ).count()
            self.stdout.write(f'- {material.name}: {usage_count} times used') 