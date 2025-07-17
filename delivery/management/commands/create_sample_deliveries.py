from django.core.management.base import BaseCommand
from django.utils import timezone
from delivery.models import DeliveryRecord, DeliveryCompany, Courier
from orders.models import Order
from users.models import User
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create sample delivery data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample delivery data...')
        
        # Get or create delivery company
        company, created = DeliveryCompany.objects.get_or_create(
            name_en='Atlas Express Delivery',
            defaults={
                'name_ar': 'أطلس إكسبريس للتوصيل',
                'base_cost': 25.0,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created delivery company: {company.name_en}')
        
        # Get or create courier
        courier_user, created = User.objects.get_or_create(
            email='courier@atlas.com',
            defaults={
                'full_name': 'Mohammed Ali',
                'phone_number': '+971507654321',
                'is_active': True
            }
        )
        
        courier, created = Courier.objects.get_or_create(
            user=courier_user,
            defaults={
                'company': company,
                'vehicle_type': 'motorcycle',
                'vehicle_number': 'DXB-1234',
                'availability': 'available',
                'rating': 4.8,
                'total_deliveries': 0,
                'successful_deliveries': 0,
                'failed_deliveries': 0
            }
        )
        if created:
            self.stdout.write(f'Created courier: {courier.user.full_name}')
        
        # Get existing orders
        orders = Order.objects.all()[:10]  # Get first 10 orders
        
        if not orders:
            self.stdout.write('No orders found. Please create some orders first.')
            return
        
        # Create delivery records
        statuses = ['assigned', 'accepted', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed']
        priorities = ['urgent', 'high', 'normal', 'low']
        
        for i, order in enumerate(orders):
            # Skip if delivery already exists
            if DeliveryRecord.objects.filter(order=order).exists():
                continue
            
            status = random.choice(statuses)
            priority = random.choice(priorities)
            
            # Calculate dates
            assigned_at = timezone.now() - timedelta(days=random.randint(0, 7))
            estimated_delivery = assigned_at + timedelta(hours=random.randint(2, 24))
            
            # Set delivery times based on status
            accepted_at = None
            picked_up_at = None
            delivered_at = None
            failed_at = None
            
            if status in ['accepted', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed']:
                accepted_at = assigned_at + timedelta(minutes=random.randint(5, 30))
            
            if status in ['picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed']:
                picked_up_at = accepted_at + timedelta(minutes=random.randint(15, 60))
            
            if status == 'delivered':
                delivered_at = picked_up_at + timedelta(hours=random.randint(1, 4))
            elif status == 'failed':
                failed_at = picked_up_at + timedelta(hours=random.randint(1, 3))
            
            delivery = DeliveryRecord.objects.create(
                order=order,
                courier=courier,
                tracking_number=f'TRK-{timezone.now().strftime("%Y%m%d")}-{i+1:03d}',
                status=status,
                priority=priority,
                assigned_at=assigned_at,
                accepted_at=accepted_at,
                picked_up_at=picked_up_at,
                delivered_at=delivered_at,
                failed_at=failed_at,
                estimated_delivery_time=estimated_delivery,
                delivery_cost=random.uniform(15.0, 50.0),
                delivery_notes=f'Sample delivery note for order {order.order_number}',
                customer_signature='Sample Signature' if status == 'delivered' else '',
                customer_rating=random.randint(3, 5) if status == 'delivered' else None,
                customer_feedback='Great service!' if status == 'delivered' else ''
            )
            
            self.stdout.write(f'Created delivery: {delivery.tracking_number} - {status}')
        
        # Update courier statistics
        total_deliveries = DeliveryRecord.objects.filter(courier=courier).count()
        successful_deliveries = DeliveryRecord.objects.filter(courier=courier, status='delivered').count()
        failed_deliveries = DeliveryRecord.objects.filter(courier=courier, status='failed').count()
        
        courier.total_deliveries = total_deliveries
        courier.successful_deliveries = successful_deliveries
        courier.failed_deliveries = failed_deliveries
        courier.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {DeliveryRecord.objects.count()} delivery records!'
            )
        )
        self.stdout.write(f'Courier statistics: {total_deliveries} total, {successful_deliveries} successful, {failed_deliveries} failed') 