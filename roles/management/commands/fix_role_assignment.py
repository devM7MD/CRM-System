from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, UserRole
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix role assignment issues and ensure all users have proper roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reassignment of roles even if user already has roles',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            # Ensure basic roles exist
            roles_to_create = {
                'Admin': 'System Administrator',
                'Seller': 'Product Seller',
                'Super Admin': 'Super Administrator',
                'Accountant': 'Financial Accountant',
                'Call Center Manager': 'Call Center Manager',
                'Call Center Agent': 'Call Center Agent',
            }
            
            created_roles = {}
            for role_name, description in roles_to_create.items():
                role, created = Role.objects.get_or_create(
                    name=role_name,
                    defaults={
                        'description': description,
                        'is_active': True,
                    }
                )
                created_roles[role_name] = role
                if created:
                    self.stdout.write(f'Created role: {role_name}')
                else:
                    self.stdout.write(f'Role already exists: {role_name}')
            
            # Get all users
            users = User.objects.all()
            self.stdout.write(f'Processing {users.count()} users...')
            
            for user in users:
                # Check if user has any roles
                existing_roles = UserRole.objects.filter(user=user, is_active=True)
                
                if not existing_roles.exists() or options['force']:
                    # Remove existing roles if forcing
                    if options['force'] and existing_roles.exists():
                        existing_roles.delete()
                        self.stdout.write(f'Removed existing roles for {user.email}')
                    
                    # Assign default role based on user type
                    if user.is_superuser:
                        default_role = 'Super Admin'
                    elif user.is_staff:
                        default_role = 'Admin'
                    else:
                        default_role = 'Seller'  # Default for regular users
                    
                    # Get the role
                    role = created_roles.get(default_role)
                    if role:
                        # Create user role assignment
                        user_role = UserRole.objects.create(
                            user=user,
                            role=role,
                            is_primary=True,
                            is_active=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Assigned {default_role} role to {user.email}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Could not find role {default_role} for {user.email}')
                        )
                else:
                    self.stdout.write(f'User {user.email} already has roles assigned')
            
            # Summary
            total_users = User.objects.count()
            users_with_roles = UserRole.objects.filter(is_active=True).values('user').distinct().count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nRole assignment complete!\n'
                    f'Total users: {total_users}\n'
                    f'Users with roles: {users_with_roles}\n'
                    f'Users without roles: {total_users - users_with_roles}'
                )
            ) 