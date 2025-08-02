from django.core.management.base import BaseCommand
from django.apps import apps
from roles.models import Permission
from django.db import transaction

class Command(BaseCommand):
    help = 'Generate comprehensive permissions for all models in the project'

    def handle(self, *args, **options):
        self.stdout.write('Generating permissions for all models...')
        
        # Define all apps and their models with permissions
        app_permissions = {
            'dashboard': {
                'Dashboard': ['read', 'manage'],
                'Activity': ['read', 'create', 'update', 'delete'],
                'Report': ['read', 'create', 'export'],
                'SystemStatus': ['read', 'manage'],
            },
            'users': {
                'User': ['create', 'read', 'update', 'delete', 'manage'],
                'UserProfile': ['read', 'update'],
                'AuditLog': ['read', 'export'],
            },
            'sellers': {
                'Seller': ['create', 'read', 'update', 'delete', 'manage'],
                'Product': ['create', 'read', 'update', 'delete', 'export', 'import'],
                'SalesChannel': ['create', 'read', 'update', 'delete'],
                'SourcingRequest': ['create', 'read', 'update', 'delete', 'approve', 'reject'],
            },
            'sourcing': {
                'SourcingRequest': ['create', 'read', 'update', 'delete', 'approve', 'reject', 'export'],
                'Supplier': ['create', 'read', 'update', 'delete', 'manage'],
            },
            'inventory': {
                'Warehouse': ['create', 'read', 'update', 'delete', 'manage'],
                'WarehouseLocation': ['create', 'read', 'update', 'delete'],
                'Stock': ['read', 'update', 'manage'],
                'InventoryRecord': ['create', 'read', 'update', 'delete', 'export'],
                'InventoryMovement': ['create', 'read', 'update', 'delete', 'export'],
            },
            'callcenter': {
                'CallLog': ['create', 'read', 'update', 'delete', 'export'],
                'AgentPerformance': ['read', 'update', 'export'],
                'Customer': ['create', 'read', 'update', 'delete'],
            },
            'packaging': {
                'Package': ['create', 'read', 'update', 'delete'],
                'PackagingTask': ['create', 'read', 'update', 'delete', 'assign'],
            },
            'delivery': {
                'Delivery': ['create', 'read', 'update', 'delete', 'assign'],
                'DeliveryCompany': ['create', 'read', 'update', 'delete', 'manage'],
                'DeliveryAgent': ['create', 'read', 'update', 'delete'],
            },
            'finance': {
                'Payment': ['create', 'read', 'update', 'delete', 'approve', 'export'],
                'Invoice': ['create', 'read', 'update', 'delete', 'export'],
                'Transaction': ['read', 'export'],
                'FinancialReport': ['read', 'create', 'export'],
            },
            'settings': {
                'Country': ['create', 'read', 'update', 'delete', 'manage'],
                'DeliveryCompany': ['create', 'read', 'update', 'delete', 'manage'],
                'SystemSetting': ['read', 'update', 'manage'],
                'AuditLog': ['read', 'export'],
            },
            'orders': {
                'Order': ['create', 'read', 'update', 'delete', 'export', 'import'],
                'OrderItem': ['create', 'read', 'update', 'delete'],
            },
            'landing': {
                'Page': ['create', 'read', 'update', 'delete', 'manage'],
                'Contact': ['read', 'delete'],
            },
            'products': {
                'Product': ['create', 'read', 'update', 'delete', 'export', 'import'],
            },
            'subscribers': {
                'Subscriber': ['create', 'read', 'update', 'delete', 'export'],
            },
            'roles': {
                'Role': ['create', 'read', 'update', 'delete', 'manage'],
                'Permission': ['create', 'read', 'update', 'delete', 'manage'],
                'RolePermission': ['create', 'read', 'update', 'delete', 'manage'],
                'UserRole': ['create', 'read', 'update', 'delete', 'manage'],
                'RoleAuditLog': ['read', 'export'],
            },
            'bug_reports': {
                'BugReport': ['create', 'read', 'update', 'delete', 'assign'],
            },
        }
        
        # Additional module-level permissions
        module_permissions = {
            'dashboard': ['access_dashboard', 'view_reports', 'manage_system'],
            'users': ['manage_users', 'view_audit_logs'],
            'sellers': ['manage_sellers', 'manage_products', 'manage_sales'],
            'sourcing': ['manage_sourcing', 'approve_requests'],
            'inventory': ['manage_inventory', 'view_stock', 'manage_warehouses'],
            'callcenter': ['manage_calls', 'view_performance'],
            'packaging': ['manage_packaging', 'assign_tasks'],
            'delivery': ['manage_delivery', 'assign_agents'],
            'finance': ['manage_finance', 'view_reports', 'approve_payments'],
            'settings': ['manage_settings', 'view_system'],
            'orders': ['manage_orders', 'import_orders', 'export_orders'],
            'landing': ['manage_website', 'view_contacts'],
            'products': ['manage_products', 'import_products'],
            'subscribers': ['manage_subscribers'],
            'roles': ['manage_roles', 'assign_permissions'],
            'bug_reports': ['manage_bugs', 'assign_reports'],
        }
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            # Create model-specific permissions
            for app_name, models in app_permissions.items():
                for model_name, permission_types in models.items():
                    for perm_type in permission_types:
                        codename = f"{perm_type}_{model_name.lower()}"
                        name = f"{perm_type.title()} {model_name}"
                        description = f"Can {perm_type} {model_name} records"
                        
                        permission, created = Permission.objects.get_or_create(
                            codename=codename,
                            defaults={
                                'name': name,
                                'description': description,
                                'permission_type': perm_type,
                                'module': app_name,
                                'model_name': model_name,
                                'is_active': True,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            # Update existing permission
                            permission.name = name
                            permission.description = description
                            permission.model_name = model_name
                            permission.save()
                            updated_count += 1
            
            # Create module-level permissions
            for module, permissions in module_permissions.items():
                for perm_name in permissions:
                    codename = f"{perm_name}_{module}"
                    name = f"{perm_name.replace('_', ' ').title()} {module.title()}"
                    description = f"Can {perm_name.replace('_', ' ')} in {module}"
                    
                    permission, created = Permission.objects.get_or_create(
                        codename=codename,
                        defaults={
                            'name': name,
                            'description': description,
                            'permission_type': 'manage',
                            'module': module,
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing permission
                        permission.name = name
                        permission.description = description
                        permission.save()
                        updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated permissions: {created_count} created, {updated_count} updated'
            )
        )
        
        # Display summary
        total_permissions = Permission.objects.count()
        self.stdout.write(f'Total permissions in database: {total_permissions}')
        
        # Show permissions by module
        self.stdout.write('\nPermissions by module:')
        for module in sorted(app_permissions.keys()):
            count = Permission.objects.filter(module=module).count()
            self.stdout.write(f'  {module}: {count} permissions') 