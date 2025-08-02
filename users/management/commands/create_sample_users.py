from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample users for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample users...')
        
        # Sample users data
        users_data = [
            {
                'email': 'seller1@atlas.com',
                'full_name': 'Ahmed Al Mansouri',
                'phone_number': '+971501234567',
                'role': 'Seller'
            },
            {
                'email': 'seller2@atlas.com',
                'full_name': 'Fatima Al Zahra',
                'phone_number': '+971502345678',
                'role': 'Seller'
            },
            {
                'email': 'seller3@atlas.com',
                'full_name': 'Omar Al Rashid',
                'phone_number': '+971503456789',
                'role': 'Seller'
            },
            {
                'email': 'admin@atlas.com',
                'full_name': 'Admin User',
                'phone_number': '+971504567890',
                'role': 'Admin'
            },
            {
                'email': 'callcenter@atlas.com',
                'full_name': 'Call Center Agent',
                'phone_number': '+971505678901',
                'role': 'Call Center Agent'
            }
        ]
        
        users_created = 0
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'full_name': user_data['full_name'],
                    'phone_number': user_data['phone_number'],
                    'is_active': True
                }
            )
            
            if created:
                # Set password
                user.set_password('Atlas123!')
                user.save()
                
                # Assign role
                role = Role.objects.filter(name=user_data['role']).first()
                if role:
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        is_primary=True,
                        is_active=True
                    )
                
                users_created += 1
                self.stdout.write(f'Created user: {user.email} with role: {user_data["role"]}')
            else:
                self.stdout.write(f'User already exists: {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {users_created} new users!')
        ) 