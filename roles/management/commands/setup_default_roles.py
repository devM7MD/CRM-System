from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up default roles with comprehensive permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up default roles with permissions...')
        
        with transaction.atomic():
            # Create default roles
            default_roles = {
                'Super Admin': {
                    'description': 'Full system access with all permissions',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': 'all'  # All permissions
                },
                'Admin': {
                    'description': 'Administrative access with most permissions',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard', 'view_reports_dashboard', 'manage_system_dashboard',
                        # Users
                        'manage_users_users', 'view_audit_logs_users',
                        # Orders
                        'manage_orders_orders', 'import_orders_orders', 'export_orders_orders',
                        # Inventory
                        'manage_inventory_inventory', 'view_stock_inventory', 'manage_warehouses_inventory',
                        # Finance
                        'manage_finance_finance', 'view_reports_finance', 'approve_payments_finance',
                        # Settings
                        'manage_settings_settings', 'view_system_settings',
                        # Roles
                        'manage_roles_roles', 'assign_permissions_roles',
                        # All read permissions
                        'read_dashboard', 'read_users', 'read_orders', 'read_inventory', 'read_finance', 'read_settings', 'read_roles'
                    ]
                },
                'Seller': {
                    'description': 'Seller access to manage products and orders',
                    'is_default': True,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard',
                        # Orders
                        'create_orders_orders', 'read_orders_orders', 'update_orders_orders', 'export_orders_orders',
                        # Products
                        'create_products_products', 'read_products_products', 'update_products_products', 'delete_products_products',
                        # Sourcing
                        'create_sourcing_sourcing', 'read_sourcing_sourcing', 'update_sourcing_sourcing',
                        # Inventory
                        'read_inventory_inventory', 'view_stock_inventory',
                        # Finance
                        'read_finance_finance', 'view_reports_finance',
                    ]
                },
                'Accountant': {
                    'description': 'Financial management and reporting access',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard', 'view_reports_dashboard',
                        # Finance
                        'manage_finance_finance', 'view_reports_finance', 'approve_payments_finance',
                        'create_payment_finance', 'read_payment_finance', 'update_payment_finance', 'delete_payment_finance', 'approve_payment_finance', 'export_payment_finance',
                        'create_invoice_finance', 'read_invoice_finance', 'update_invoice_finance', 'delete_invoice_finance', 'export_invoice_finance',
                        'read_transaction_finance', 'export_transaction_finance',
                        'read_financialreport_finance', 'create_financialreport_finance', 'export_financialreport_finance',
                        # Orders (read only for financial data)
                        'read_orders_orders', 'export_orders_orders',
                    ]
                },
                'Call Center Agent': {
                    'description': 'Customer service and call management',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard',
                        # Call Center
                        'manage_calls_callcenter', 'view_performance_callcenter',
                        'create_calllog_callcenter', 'read_calllog_callcenter', 'update_calllog_callcenter', 'export_calllog_callcenter',
                        'read_agentperformance_callcenter', 'update_agentperformance_callcenter', 'export_agentperformance_callcenter',
                        'create_customer_callcenter', 'read_customer_callcenter', 'update_customer_callcenter',
                        # Orders (read and update for customer service)
                        'read_orders_orders', 'update_orders_orders',
                        # Users (read only for customer info)
                        'read_users_users',
                    ]
                },
                'Call Center Manager': {
                    'description': 'Call center management and supervision',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard', 'view_reports_dashboard',
                        # Call Center
                        'manage_calls_callcenter', 'view_performance_callcenter',
                        'create_calllog_callcenter', 'read_calllog_callcenter', 'update_calllog_callcenter', 'delete_calllog_callcenter', 'export_calllog_callcenter',
                        'read_agentperformance_callcenter', 'update_agentperformance_callcenter', 'export_agentperformance_callcenter',
                        'create_customer_callcenter', 'read_customer_callcenter', 'update_customer_callcenter', 'delete_customer_callcenter',
                        # Orders (full access for customer service)
                        'read_orders_orders', 'update_orders_orders', 'export_orders_orders',
                        # Users (read only for customer info)
                        'read_users_users',
                    ]
                },
                'Delivery Agent': {
                    'description': 'Delivery and shipping management',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard',
                        # Delivery
                        'manage_delivery_delivery', 'assign_agents_delivery',
                        'create_delivery_delivery', 'read_delivery_delivery', 'update_delivery_delivery',
                        'read_deliverycompany_delivery',
                        'read_deliveryagent_delivery',
                        # Orders (read and update for delivery status)
                        'read_orders_orders', 'update_orders_orders',
                    ]
                },
                'Stock Keeper': {
                    'description': 'Inventory and warehouse management',
                    'is_default': False,
                    'is_protected': True,
                    'permissions': [
                        # Dashboard
                        'access_dashboard_dashboard',
                        # Inventory
                        'manage_inventory_inventory', 'view_stock_inventory', 'manage_warehouses_inventory',
                        'create_warehouse_inventory', 'read_warehouse_inventory', 'update_warehouse_inventory', 'delete_warehouse_inventory', 'manage_warehouse_inventory',
                        'create_warehouselocation_inventory', 'read_warehouselocation_inventory', 'update_warehouselocation_inventory', 'delete_warehouselocation_inventory',
                        'read_stock_inventory', 'update_stock_inventory', 'manage_stock_inventory',
                        'create_inventoryrecord_inventory', 'read_inventoryrecord_inventory', 'update_inventoryrecord_inventory', 'delete_inventoryrecord_inventory', 'export_inventoryrecord_inventory',
                        'create_inventorymovement_inventory', 'read_inventorymovement_inventory', 'update_inventorymovement_inventory', 'delete_inventorymovement_inventory', 'export_inventorymovement_inventory',
                        # Products (read only)
                        'read_products_products',
                        # Orders (read only for inventory planning)
                        'read_orders_orders',
                    ]
                },
            }
            
            created_roles = 0
            updated_roles = 0
            
            for role_name, role_data in default_roles.items():
                role, created = Role.objects.get_or_create(
                    name=role_name,
                    defaults={
                        'description': role_data['description'],
                        'is_default': role_data['is_default'],
                        'is_protected': role_data['is_protected'],
                        'is_active': True,
                    }
                )
                
                if created:
                    created_roles += 1
                    self.stdout.write(f'Created role: {role_name}')
                else:
                    updated_roles += 1
                    self.stdout.write(f'Updated role: {role_name}')
                
                # Assign permissions
                if role_data['permissions'] == 'all':
                    # Super Admin gets all permissions
                    all_permissions = Permission.objects.filter(is_active=True)
                    for permission in all_permissions:
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=permission,
                            defaults={'granted': True}
                        )
                else:
                    # Other roles get specific permissions
                    for perm_codename in role_data['permissions']:
                        try:
                            permission = Permission.objects.get(codename=perm_codename, is_active=True)
                            RolePermission.objects.get_or_create(
                                role=role,
                                permission=permission,
                                defaults={'granted': True}
                            )
                        except Permission.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f'Permission {perm_codename} not found for role {role_name}')
                            )
            
            # Assign default roles to existing users
            admin_role = Role.objects.get(name='Admin')
            seller_role = Role.objects.get(name='Seller')
            
            # Assign Admin role to superusers
            superusers = User.objects.filter(is_superuser=True)
            for user in superusers:
                if not user.user_roles.filter(role=admin_role).exists():
                    from roles.models import UserRole
                    UserRole.objects.create(
                        user=user,
                        role=admin_role,
                        is_primary=True,
                        assigned_by=user
                    )
                    self.stdout.write(f'Assigned Admin role to superuser: {user.email}')
            
            # Assign Seller role to regular users (non-superusers)
            regular_users = User.objects.filter(is_superuser=False)
            for user in regular_users:
                if not user.user_roles.filter(role=seller_role).exists():
                    from roles.models import UserRole
                    UserRole.objects.create(
                        user=user,
                        role=seller_role,
                        is_primary=True,
                        assigned_by=user
                    )
                    self.stdout.write(f'Assigned Seller role to user: {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up roles: {created_roles} created, {updated_roles} updated'
            )
        )
        
        # Display summary
        total_roles = Role.objects.count()
        total_permissions = Permission.objects.count()
        total_role_permissions = RolePermission.objects.count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Total roles: {total_roles}')
        self.stdout.write(f'  Total permissions: {total_permissions}')
        self.stdout.write(f'  Total role permissions: {total_role_permissions}')
        
        # Show roles and their permission counts
        self.stdout.write(f'\nRoles and permissions:')
        for role in Role.objects.all():
            perm_count = role.get_permission_count()
            user_count = role.get_user_count()
            self.stdout.write(f'  {role.name}: {perm_count} permissions, {user_count} users') 