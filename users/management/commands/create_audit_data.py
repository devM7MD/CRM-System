from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import AuditLog, User
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create sample audit log data for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'full_name': 'Test User',
                'phone_number': '1234567890',
                'is_active': True
            }
        )

        # Sample audit log entries
        audit_entries = [
            {
                'action': 'login',
                'entity_type': 'User',
                'entity_id': str(user.id),
                'description': f'User {user.get_full_name()} logged in successfully',
                'user': user,
                'timestamp': timezone.now() - timedelta(minutes=5)
            },
            {
                'action': 'create',
                'entity_type': 'Order',
                'entity_id': 'ORD-202508-001',
                'description': 'New order created by system',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=1)
            },
            {
                'action': 'update',
                'entity_type': 'User',
                'entity_id': str(user.id),
                'description': f'User profile updated for {user.get_full_name()}',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=2)
            },
            {
                'action': 'delete',
                'entity_type': 'Product',
                'entity_id': 'PROD-001',
                'description': 'Product deleted from inventory',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=3)
            },
            {
                'action': 'permission_change',
                'entity_type': 'Role',
                'entity_id': 'ROLE-001',
                'description': 'User permissions modified',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=4)
            },
            {
                'action': 'status_change',
                'entity_type': 'Order',
                'entity_id': 'ORD-202508-002',
                'description': 'Order status changed to completed',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=5)
            },
            {
                'action': 'view',
                'entity_type': 'Dashboard',
                'entity_id': 'DASH-001',
                'description': 'Dashboard accessed by user',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=6)
            },
            {
                'action': 'logout',
                'entity_type': 'User',
                'entity_id': str(user.id),
                'description': f'User {user.get_full_name()} logged out',
                'user': user,
                'timestamp': timezone.now() - timedelta(hours=7)
            },
        ]

        # Create audit log entries
        for entry_data in audit_entries:
            AuditLog.objects.get_or_create(
                action=entry_data['action'],
                entity_type=entry_data['entity_type'],
                entity_id=entry_data['entity_id'],
                description=entry_data['description'],
                user=entry_data['user'],
                timestamp=entry_data['timestamp'],
                defaults={
                    'ip_address': '127.0.0.1',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(audit_entries)} audit log entries')
        ) 