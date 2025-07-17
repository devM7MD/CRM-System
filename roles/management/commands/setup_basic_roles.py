from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission, UserRole
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up basic roles for the CRM system'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Setting up basic roles...')
            
            # Create basic roles
            roles_data = [
                {
                    'name': 'Super Admin',
                    'role_type': 'super_admin',
                    'description': 'System Super Administrator with full access',
                    'is_active': True,
                    'is_default': False,
                },
                {
                    'name': 'Admin',
                    'role_type': 'admin',
                    'description': 'System Administrator',
                    'is_active': True,
                    'is_default': False,
                },
                {
                    'name': 'Seller',
                    'role_type': 'seller',
                    'description': 'Product seller with inventory and order management',
                    'is_active': True,
                    'is_default': False,
                },
                {
                    'name': 'Manager',
                    'role_type': 'manager',
                    'description': 'General manager with oversight capabilities',
                    'is_active': True,
                    'is_default': False,
                },
                {
                    'name': 'Support',
                    'role_type': 'support',
                    'description': 'Customer support representative',
                    'is_active': True,
                    'is_default': False,
                },
            ]
            
            created_roles = {}
            for role_data in roles_data:
                role, created = Role.objects.get_or_create(
                    name=role_data['name'],
                    defaults=role_data
                )
                created_roles[role.name] = role
                if created:
                    self.stdout.write(f'Created role: {role.name}')
                else:
                    self.stdout.write(f'Role already exists: {role.name}')
            
            # Create basic permissions
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
                
                # Warehouse permissions
                {'name': 'View Warehouses', 'codename': 'view_warehouses', 'permission_type': 'read', 'module': 'inventory'},
                {'name': 'Create Warehouses', 'codename': 'create_warehouses', 'permission_type': 'create', 'module': 'inventory'},
                {'name': 'Edit Warehouses', 'codename': 'edit_warehouses', 'permission_type': 'update', 'module': 'inventory'},
                {'name': 'Delete Warehouses', 'codename': 'delete_warehouses', 'permission_type': 'delete', 'module': 'inventory'},
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
                'Admin': [
                    'view_dashboard', 'access_analytics',
                    'view_users', 'create_users', 'edit_users',
                    'view_roles', 'create_roles', 'edit_roles',
                    'view_orders', 'create_orders', 'edit_orders',
                    'view_inventory', 'create_products', 'edit_products',
                    'view_warehouses', 'create_warehouses', 'edit_warehouses',
                ],
                'Seller': [
                    'view_dashboard',
                    'view_orders', 'create_orders', 'edit_orders',
                    'view_inventory', 'create_products', 'edit_products',
                ],
                'Manager': [
                    'view_dashboard', 'access_analytics',
                    'view_users', 'edit_users',
                    'view_orders', 'create_orders', 'edit_orders',
                    'view_inventory', 'create_products', 'edit_products',
                    'view_warehouses', 'create_warehouses', 'edit_warehouses',
                ],
                'Support': [
                    'view_dashboard',
                    'view_orders', 'edit_orders',
                    'view_inventory',
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
            
            # Assign roles to existing users
            user_roles = {
                'admin@devm7md.xyz': 'Super Admin',
                'admin1@devm7md.xyz': 'Admin',
                'seller@atlas.com': 'Seller',
                'accountant@atlas.com': 'Manager',
                'stock@atlas.com': 'Manager',
                'delivery@atlas.com': 'Support',
            }
            
            for email, role_name in user_roles.items():
                try:
                    user = User.objects.get(email=email)
                    role = created_roles.get(role_name)
                    if role:
                        # Remove existing primary roles
                        UserRole.objects.filter(user=user, is_primary=True).update(is_primary=False)
                        
                        # Create new user role assignment
                        user_role, created = UserRole.objects.get_or_create(
                            user=user,
                            role=role,
                            defaults={'is_primary': True, 'is_active': True}
                        )
                        if created:
                            self.stdout.write(f'Assigned {role_name} role to {email}')
                        else:
                            user_role.is_primary = True
                            user_role.is_active = True
                            user_role.save()
                            self.stdout.write(f'Updated {role_name} role for {email}')
                except User.DoesNotExist:
                    self.stdout.write(f'User {email} not found')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully set up basic roles and permissions!')
            ) 