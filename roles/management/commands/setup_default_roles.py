from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up default Super Admin and Seller roles that cannot be deleted'

    def handle(self, *args, **options):
        self.stdout.write('Setting up default Super Admin and Seller roles...')
        
        # Create only Super Admin and Seller roles
        roles_data = [
            {
                'name': 'Super Admin',
                'role_type': 'super_admin',
                'description': 'System Super Administrator with full access to all features',
                'is_default': True,
                'is_protected': True,  # Cannot be deleted
            },
            {
                'name': 'Seller',
                'role_type': 'seller',
                'description': 'Product seller with inventory and order management access',
                'is_default': True,
                'is_protected': True,  # Cannot be deleted
            },
        ]
        
        created_roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            # Update existing roles to be protected
            if not created:
                role.is_protected = True
                role.is_default = True
                role.save()
            
            created_roles[role.name] = role
            if created:
                self.stdout.write(f'Created protected role: {role.name}')
            else:
                self.stdout.write(f'Updated existing role to protected: {role.name}')
        
        # Create permissions
        permissions_data = [
            # Dashboard permissions
            {'name': 'View Dashboard', 'codename': 'view_dashboard', 'permission_type': 'read', 'module': 'dashboard'},
            {'name': 'Access Analytics', 'codename': 'access_analytics', 'permission_type': 'read', 'module': 'dashboard'},
            
            # User management permissions
            {'name': 'View Users', 'codename': 'view_users', 'permission_type': 'read', 'module': 'users'},
            {'name': 'Create Users', 'codename': 'create_users', 'permission_type': 'create', 'module': 'users'},
            {'name': 'Edit Users', 'codename': 'edit_users', 'permission_type': 'update', 'module': 'users'},
            {'name': 'Delete Users', 'codename': 'delete_users', 'permission_type': 'delete', 'module': 'users'},
            
            # Role management permissions
            {'name': 'View Roles', 'codename': 'view_roles', 'permission_type': 'read', 'module': 'roles'},
            {'name': 'Create Roles', 'codename': 'create_roles', 'permission_type': 'create', 'module': 'roles'},
            {'name': 'Edit Roles', 'codename': 'edit_roles', 'permission_type': 'update', 'module': 'roles'},
            {'name': 'Delete Roles', 'codename': 'delete_roles', 'permission_type': 'delete', 'module': 'roles'},
            
            # Order management permissions
            {'name': 'View Orders', 'codename': 'view_orders', 'permission_type': 'read', 'module': 'orders'},
            {'name': 'Create Orders', 'codename': 'create_orders', 'permission_type': 'create', 'module': 'orders'},
            {'name': 'Edit Orders', 'codename': 'edit_orders', 'permission_type': 'update', 'module': 'orders'},
            {'name': 'Delete Orders', 'codename': 'delete_orders', 'permission_type': 'delete', 'module': 'orders'},
            
            # Inventory permissions
            {'name': 'View Inventory', 'codename': 'view_inventory', 'permission_type': 'read', 'module': 'inventory'},
            {'name': 'Create Products', 'codename': 'create_products', 'permission_type': 'create', 'module': 'inventory'},
            {'name': 'Edit Products', 'codename': 'edit_products', 'permission_type': 'update', 'module': 'inventory'},
            {'name': 'Delete Products', 'codename': 'delete_products', 'permission_type': 'delete', 'module': 'inventory'},
            
            # Finance permissions
            {'name': 'View Finance', 'codename': 'view_finance', 'permission_type': 'read', 'module': 'finance'},
            {'name': 'Create Payments', 'codename': 'create_payments', 'permission_type': 'create', 'module': 'finance'},
            {'name': 'Edit Payments', 'codename': 'edit_payments', 'permission_type': 'update', 'module': 'finance'},
            {'name': 'Delete Payments', 'codename': 'delete_payments', 'permission_type': 'delete', 'module': 'finance'},
            
            # Sourcing permissions
            {'name': 'View Sourcing', 'codename': 'view_sourcing', 'permission_type': 'read', 'module': 'sourcing'},
            {'name': 'Create Sourcing Requests', 'codename': 'create_sourcing_requests', 'permission_type': 'create', 'module': 'sourcing'},
            {'name': 'Edit Sourcing Requests', 'codename': 'edit_sourcing_requests', 'permission_type': 'update', 'module': 'sourcing'},
            {'name': 'Delete Sourcing Requests', 'codename': 'delete_sourcing_requests', 'permission_type': 'delete', 'module': 'sourcing'},
        ]
        
        created_permissions = {}
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data
            )
            created_permissions[permission.codename] = permission
            if created:
                self.stdout.write(f'Created permission: {permission.name}')
            else:
                self.stdout.write(f'Permission already exists: {permission.name}')
        
        # Assign permissions to roles
        role_permissions = {
            'Super Admin': [perm.codename for perm in created_permissions.values()],  # All permissions
            'Seller': [
                'view_dashboard',
                'view_orders', 'create_orders', 'edit_orders',
                'view_inventory', 'create_products', 'edit_products',
                'view_sourcing', 'create_sourcing_requests', 'edit_sourcing_requests',
            ],
        }
        
        for role_name, permission_codenames in role_permissions.items():
            if role_name in created_roles:
                role = created_roles[role_name]
                # Clear existing permissions
                RolePermission.objects.filter(role=role).delete()
                
                # Add new permissions
                for codename in permission_codenames:
                    if codename in created_permissions:
                        permission = created_permissions[codename]
                        RolePermission.objects.create(
                            role=role,
                            permission=permission,
                            granted=True
                        )
                
                self.stdout.write(f'Assigned {len(permission_codenames)} permissions to {role_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up default Super Admin and Seller roles!')
        ) 