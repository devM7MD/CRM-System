from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from delivery.models import (
    DeliveryCompany, Courier, DeliveryRecord, DeliveryPerformance,
    DeliveryStatusHistory, CourierSession, CourierLocation
)
from orders.models import Order
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample delivery data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--couriers',
            type=int,
            default=5,
            help='Number of couriers to create'
        )
        parser.add_argument(
            '--deliveries',
            type=int,
            default=50,
            help='Number of deliveries to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample delivery data...')
        
        # Create delivery company
        company, created = DeliveryCompany.objects.get_or_create(
            name_en="Atlas Express Delivery",
            name_ar="أطلس إكسبريس للتوصيل",
            defaults={
                'base_cost': Decimal('15.00'),
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created delivery company: {company.name_en}')
        
        # Create couriers
        couriers = []
        for i in range(options['couriers']):
            # Create user for courier
            user, created = User.objects.get_or_create(
                email=f'courier{i+1}@atlas.com',
                defaults={
                    'full_name': f'Courier {i+1}',
                    'phone_number': f'+97150{random.randint(1000000, 9999999)}',
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create courier profile
            courier, created = Courier.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP{i+1:03d}',
                    'delivery_company': company,
                    'phone_number': f'+97150{random.randint(1000000, 9999999)}',
                    'vehicle_type': random.choice(['sedan', 'suv', 'van', 'motorcycle']),
                    'vehicle_number': f'DXB-{random.randint(1000, 9999)}',
                    'license_number': f'LIC{random.randint(100000, 999999)}',
                    'status': 'active',
                    'availability': random.choice(['available', 'busy', 'offline']),
                    'max_daily_deliveries': random.randint(30, 80),
                    'rating': Decimal(str(random.uniform(3.5, 5.0))),
                    'total_deliveries': random.randint(50, 500),
                    'successful_deliveries': 0,
                    'failed_deliveries': 0,
                }
            )
            
            if created:
                # Set realistic delivery statistics
                total = courier.total_deliveries
                successful = random.randint(int(total * 0.85), int(total * 0.98))  # 85-98% success rate
                failed = total - successful
                
                courier.successful_deliveries = successful
                courier.failed_deliveries = failed
                courier.save()
                self.stdout.write(f'Created courier: {courier.user.get_full_name()}')
            
            couriers.append(courier)
        
        # Create delivery records
        orders = Order.objects.all()
        if not orders.exists():
            self.stdout.write('No orders found. Please create some orders first.')
            return
        
        deliveries_created = 0
        for i in range(options['deliveries']):
            order = random.choice(orders)
            
            # Check if delivery already exists for this order
            if DeliveryRecord.objects.filter(order=order).exists():
                continue
            
            courier = random.choice(couriers)
            status = random.choice(['assigned', 'accepted', 'picked_up', 'delivered', 'failed'])
            
            # Create delivery record
            delivery = DeliveryRecord.objects.create(
                order=order,
                delivery_company=company,
                courier=courier,
                tracking_number=f'TRK{random.randint(100000, 999999)}',
                status=status,
                priority=random.choice(['low', 'normal', 'high', 'urgent']),
                delivery_cost=Decimal(str(random.uniform(10.0, 50.0))),
                delivery_notes=f'Sample delivery note {i+1}',
            )
            
            # Set timestamps based on status
            now = timezone.now()
            if status in ['accepted', 'picked_up', 'delivered', 'failed']:
                delivery.accepted_at = now - timedelta(hours=random.randint(1, 6))
            
            if status in ['picked_up', 'delivered', 'failed']:
                delivery.picked_up_at = delivery.accepted_at + timedelta(minutes=random.randint(10, 30))
            
            if status in ['delivered', 'failed']:
                delivery.delivered_at = delivery.picked_up_at + timedelta(minutes=random.randint(15, 60))
            
            if status == 'failed':
                delivery.failed_at = delivery.picked_up_at + timedelta(minutes=random.randint(15, 60))
            
            delivery.save()
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                delivery=delivery,
                status=status,
                changed_by=courier.user,
                notes=f'Status changed to {status}',
                timestamp=delivery.assigned_at
            )
            
            deliveries_created += 1
        
        # Create performance records
        for courier in couriers:
            for i in range(30):  # Last 30 days
                date = timezone.now().date() - timedelta(days=i)
                
                # Get deliveries for this date
                daily_deliveries = DeliveryRecord.objects.filter(
                    courier=courier,
                    assigned_at__date=date
                )
                
                if daily_deliveries.exists():
                    total_deliveries = daily_deliveries.count()
                    successful_deliveries = daily_deliveries.filter(status='delivered').count()
                    failed_deliveries = daily_deliveries.filter(status='failed').count()
                    
                    # Create performance record
                    DeliveryPerformance.objects.get_or_create(
                        courier=courier,
                        date=date,
                        defaults={
                            'total_deliveries': total_deliveries,
                            'successful_deliveries': successful_deliveries,
                            'failed_deliveries': failed_deliveries,
                            'total_distance': Decimal(str(random.uniform(50.0, 200.0))),
                            'total_time': random.randint(300, 1200),  # minutes
                            'average_delivery_time': random.randint(15, 45),
                            'customer_rating': Decimal(str(random.uniform(3.5, 5.0))),
                        }
                    )
        
        # Create courier sessions
        for courier in couriers:
            # Create current session
            CourierSession.objects.get_or_create(
                courier=courier,
                logout_time__isnull=True,
                defaults={
                    'login_time': timezone.now() - timedelta(hours=random.randint(1, 8)),
                    'status': random.choice(['active', 'break']),
                    'device_info': 'Sample Device Info',
                    'ip_address': '192.168.1.100',
                }
            )
            
            # Create some location records
            for i in range(10):
                CourierLocation.objects.create(
                    courier=courier,
                    latitude=Decimal(str(25.2048 + random.uniform(-0.1, 0.1))),  # Dubai area
                    longitude=Decimal(str(55.2708 + random.uniform(-0.1, 0.1))),
                    accuracy=Decimal(str(random.uniform(5.0, 50.0))),
                    battery_level=random.randint(20, 100),
                    connection_type=random.choice(['wifi', 'cellular']),
                    speed=Decimal(str(random.uniform(0.0, 60.0))),
                    heading=Decimal(str(random.uniform(0.0, 360.0))),
                    timestamp=timezone.now() - timedelta(minutes=i*30)
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(couriers)} couriers and {deliveries_created} deliveries'
            )
        ) 