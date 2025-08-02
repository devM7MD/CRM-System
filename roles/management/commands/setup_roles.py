from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial roles and permissions for the CRM system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial roles and permissions...')
        
        # Create roles based on task folders
        roles_data = [
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
        
        created_roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            # Update existing roles to be protected
            if not created:
                role.is_protected = True
                role.save()
            
            created_roles[role.name] = role
            if created:
                self.stdout.write(f'Created role: {role.name}')
            else:
                self.stdout.write(f'Updated role: {role.name} (now protected)')
        
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
            
            # Delivery permissions
            {'name': 'View Delivery', 'codename': 'view_delivery', 'permission_type': 'read', 'module': 'delivery'},
            {'name': 'Create Deliveries', 'codename': 'create_deliveries', 'permission_type': 'create', 'module': 'delivery'},
            {'name': 'Edit Deliveries', 'codename': 'edit_deliveries', 'permission_type': 'update', 'module': 'delivery'},
            {'name': 'Delete Deliveries', 'codename': 'delete_deliveries', 'permission_type': 'delete', 'module': 'delivery'},
            
            # Call Center permissions
            {'name': 'View Call Center', 'codename': 'view_callcenter', 'permission_type': 'read', 'module': 'callcenter'},
            {'name': 'Create Call Logs', 'codename': 'create_call_logs', 'permission_type': 'create', 'module': 'callcenter'},
            {'name': 'Edit Call Logs', 'codename': 'edit_call_logs', 'permission_type': 'update', 'module': 'callcenter'},
            {'name': 'Delete Call Logs', 'codename': 'delete_call_logs', 'permission_type': 'delete', 'module': 'callcenter'},
            
            # Packaging permissions
            {'name': 'View Packaging', 'codename': 'view_packaging', 'permission_type': 'read', 'module': 'packaging'},
            {'name': 'Create Packaging Records', 'codename': 'create_packaging_records', 'permission_type': 'create', 'module': 'packaging'},
            {'name': 'Edit Packaging Records', 'codename': 'edit_packaging_records', 'permission_type': 'update', 'module': 'packaging'},
            {'name': 'Delete Packaging Records', 'codename': 'delete_packaging_records', 'permission_type': 'delete', 'module': 'packaging'},
            
            # Bug Reports permissions
            {'name': 'View Bug Reports', 'codename': 'view_bug_reports', 'permission_type': 'read', 'module': 'bug_reports'},
            {'name': 'Create Bug Reports', 'codename': 'create_bug_reports', 'permission_type': 'create', 'module': 'bug_reports'},
            {'name': 'Edit Bug Reports', 'codename': 'edit_bug_reports', 'permission_type': 'update', 'module': 'bug_reports'},
            {'name': 'Delete Bug Reports', 'codename': 'delete_bug_reports', 'permission_type': 'delete', 'module': 'bug_reports'},
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
        
        # Assign permissions to roles based on task folders
        role_permissions = {
            'Super Admin': [perm.codename for perm in created_permissions.values()],  # All permissions
            'Admin': [
                'view_dashboard', 'access_analytics',
                'view_users', 'create_users', 'edit_users',
                'view_roles', 'create_roles', 'edit_roles',
                'view_orders', 'create_orders', 'edit_orders',
                'view_inventory', 'create_products', 'edit_products',
                'view_finance', 'create_payments', 'edit_payments',
                'view_sourcing', 'create_sourcing_requests', 'edit_sourcing_requests',
                'view_delivery', 'create_deliveries', 'edit_deliveries',
                'view_callcenter', 'create_call_logs', 'edit_call_logs',
                'view_packaging', 'create_packaging_records', 'edit_packaging_records',
                'view_bug_reports', 'create_bug_reports', 'edit_bug_reports',
            ],
            'Seller': [
                'view_dashboard',
                'view_orders', 'create_orders', 'edit_orders',
                'view_inventory', 'create_products', 'edit_products',
                'view_sourcing', 'create_sourcing_requests', 'edit_sourcing_requests',
                'view_delivery', 'create_deliveries', 'edit_deliveries',
                'view_finance', 'create_payments', 'edit_payments',
            ],
            'Accountant': [
                'view_dashboard',
                'view_finance', 'create_payments', 'edit_payments', 'delete_payments',
                'view_orders',
            ],
            'Call Center Agent': [
                'view_dashboard',
                'view_orders', 'edit_orders',
                'view_callcenter', 'create_call_logs', 'edit_call_logs',
            ],
            'Call Center Manager': [
                'view_dashboard',
                'view_orders', 'create_orders', 'edit_orders',
                'view_callcenter', 'create_call_logs', 'edit_call_logs', 'delete_call_logs',
                'view_users',
            ],
            'Delivery Agent': [
                'view_dashboard',
                'view_orders', 'edit_orders',
                'view_delivery', 'create_deliveries', 'edit_deliveries',
            ],
            'Stock Keeper': [
                'view_dashboard',
                'view_inventory', 'create_products', 'edit_products', 'delete_products',
                'view_orders',
                'view_packaging', 'create_packaging_records', 'edit_packaging_records',
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
            self.style.SUCCESS('Successfully set up roles and permissions!')
        ) 