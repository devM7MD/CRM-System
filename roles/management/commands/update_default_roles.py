from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Update existing roles to be protected and create new default roles'

    def handle(self, *args, **options):
        self.stdout.write('Updating roles to be protected and creating default roles...')
        
        # Define all default roles that should be protected
        default_roles = [
            {
                'name': 'Super Admin',
                'role_type': 'super_admin',
                'description': 'System Super Administrator with full access to all features and system settings',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Admin',
                'role_type': 'admin',
                'description': 'System Administrator with administrative privileges and user management',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Seller',
                'role_type': 'seller',
                'description': 'Product seller with inventory, orders, sales channels, sourcing, delivery, and financial management access',
                'is_default': True,
                'is_protected': True,
            },
            {
                'name': 'Accountant',
                'role_type': 'accountant',
                'description': 'Financial accountant with access to financial reports, payments, and accounting features',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Call Center Agent',
                'role_type': 'call_center_agent',
                'description': 'Customer service representative for phone support and order management',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Call Center Manager',
                'role_type': 'call_center_manager',
                'description': 'Manager of call center operations, staff management, and performance monitoring',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Delivery Agent',
                'role_type': 'delivery_agent',
                'description': 'Delivery personnel responsible for order delivery and tracking',
                'is_default': False,
                'is_protected': True,
            },
            {
                'name': 'Stock Keeper',
                'role_type': 'stock_keeper',
                'description': 'Inventory manager responsible for stock management, warehouse operations, and inventory tracking',
                'is_default': False,
                'is_protected': True,
            },
        ]
        
        # Update or create roles
        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if not created:
                # Update existing role to be protected
                role.is_protected = True
                role.role_type = role_data['role_type']
                role.description = role_data['description']
                role.is_default = role_data['is_default']
                role.save()
                self.stdout.write(f'Updated role: {role.name} (now protected)')
            else:
                self.stdout.write(f'Created new role: {role.name}')
        
        # Make all existing roles protected
        existing_roles = Role.objects.all()
        for role in existing_roles:
            if not role.is_protected:
                role.is_protected = True
                role.save()
                self.stdout.write(f'Made existing role protected: {role.name}')
        
        # Assign roles to existing users if they don't have any
        users_without_roles = User.objects.filter(user_roles__isnull=True)
        seller_role = Role.objects.filter(name='Seller', is_active=True).first()
        
        if seller_role:
            for user in users_without_roles:
                if not user.is_superuser:
                    # Assign Seller role to regular users
                    from roles.models import UserRole
                    UserRole.objects.create(
                        user=user,
                        role=seller_role,
                        is_primary=True,
                        is_active=True
                    )
                    self.stdout.write(f'Assigned Seller role to user: {user.email}')
        
        # Assign Admin role to superusers if they don't have it
        admin_role = Role.objects.filter(name='Admin', is_active=True).first()
        if admin_role:
            superusers = User.objects.filter(is_superuser=True)
            for user in superusers:
                if not user.user_roles.filter(role__name='Admin').exists():
                    from roles.models import UserRole
                    UserRole.objects.create(
                        user=user,
                        role=admin_role,
                        is_primary=True,
                        is_active=True
                    )
                    self.stdout.write(f'Assigned Admin role to superuser: {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated roles and assigned default roles to users!')
        ) 