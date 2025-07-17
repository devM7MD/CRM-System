from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission, UserRole
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up basic permissions and roles for the CRM system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up permissions and roles...')
        
        # Create basic permissions
        permissions_data = [
            # Dashboard permissions
            ('dashboard_view', 'View Dashboard', 'View main dashboard', 'read', 'dashboard'),
            ('dashboard_edit', 'Edit Dashboard', 'Edit dashboard settings', 'update', 'dashboard'),
            
            # User management permissions
            ('users_view', 'View Users', 'View user list and details', 'read', 'users'),
            ('users_create', 'Create Users', 'Create new users', 'create', 'users'),
            ('users_edit', 'Edit Users', 'Edit user information', 'update', 'users'),
            ('users_delete', 'Delete Users', 'Delete users', 'delete', 'users'),
            
            # Order management permissions
            ('orders_view', 'View Orders', 'View order list and details', 'read', 'orders'),
            ('orders_create', 'Create Orders', 'Create new orders', 'create', 'orders'),
            ('orders_edit', 'Edit Orders', 'Edit order information', 'update', 'orders'),
            ('orders_delete', 'Delete Orders', 'Delete orders', 'delete', 'orders'),
            
            # Inventory permissions
            ('inventory_view', 'View Inventory', 'View inventory items', 'read', 'inventory'),
            ('inventory_create', 'Create Inventory', 'Add new inventory items', 'create', 'inventory'),
            ('inventory_edit', 'Edit Inventory', 'Edit inventory items', 'update', 'inventory'),
            ('inventory_delete', 'Delete Inventory', 'Delete inventory items', 'delete', 'inventory'),
            
            # Seller permissions
            ('sellers_view', 'View Sellers', 'View seller information', 'read', 'sellers'),
            ('sellers_create', 'Create Sellers', 'Create new sellers', 'create', 'sellers'),
            ('sellers_edit', 'Edit Sellers', 'Edit seller information', 'update', 'sellers'),
            ('sellers_delete', 'Delete Sellers', 'Delete sellers', 'delete', 'sellers'),
            
            # Finance permissions
            ('finance_view', 'View Finance', 'View financial reports', 'read', 'finance'),
            ('finance_edit', 'Edit Finance', 'Edit financial data', 'update', 'finance'),
            
            # Role management permissions
            ('roles_view', 'View Roles', 'View role information', 'read', 'roles'),
            ('roles_create', 'Create Roles', 'Create new roles', 'create', 'roles'),
            ('roles_edit', 'Edit Roles', 'Edit role information', 'update', 'roles'),
            ('roles_delete', 'Delete Roles', 'Delete roles', 'delete', 'roles'),
            
            # Admin permissions
            ('admin_access', 'Admin Access', 'Access admin panel', 'read', 'admin'),
        ]
        
        created_permissions = []
        for codename, name, description, permission_type, module in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'description': description,
                    'permission_type': permission_type,
                    'module': module,
                    'is_active': True
                }
            )
            created_permissions.append(permission)
            if created:
                self.stdout.write(f'Created permission: {name}')
        
        # Create basic roles if they don't exist
        roles_data = [
            ('Super Admin', 'super_admin', 'Full system access with all permissions'),
            ('Admin', 'admin', 'Administrative access with most permissions'),
            ('Seller', 'seller', 'Seller access for managing products and orders'),
            ('Livreur', 'livreur', 'Delivery personnel access'),
            ('Accountant', 'accountant', 'Financial and accounting access'),
            ('Stock Manager', 'stock_manager', 'Inventory and stock management access'),
            ('Teleconsultant', 'teleconsultant', 'Customer service and support access'),
            ('Call Center Manager', 'callcenter_manager', 'Call center management access'),
        ]
        
        created_roles = []
        for name, role_type, description in roles_data:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={
                    'role_type': role_type,
                    'description': description,
                    'is_active': True
                }
            )
            created_roles.append(role)
            if created:
                self.stdout.write(f'Created role: {name}')
        
        # Assign permissions to roles
        role_permissions = {
            'Super Admin': [p.codename for p in created_permissions],  # All permissions
            'Admin': [
                'dashboard_view', 'dashboard_edit',
                'users_view', 'users_create', 'users_edit',
                'orders_view', 'orders_create', 'orders_edit',
                'inventory_view', 'inventory_create', 'inventory_edit',
                'sellers_view', 'sellers_create', 'sellers_edit',
                'finance_view', 'finance_edit',
                'roles_view', 'roles_create', 'roles_edit',
                'admin_access'
            ],
            'Seller': [
                'dashboard_view',
                'orders_view', 'orders_create', 'orders_edit',
                'inventory_view', 'inventory_create', 'inventory_edit',
                'sellers_view', 'sellers_edit'
            ],
            'Livreur': [
                'dashboard_view',
                'orders_view', 'orders_edit'
            ],
            'Accountant': [
                'dashboard_view',
                'orders_view',
                'finance_view', 'finance_edit'
            ],
            'Stock Manager': [
                'dashboard_view',
                'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_delete',
                'orders_view'
            ],
            'Teleconsultant': [
                'dashboard_view',
                'orders_view', 'orders_edit',
                'users_view'
            ],
            'Call Center Manager': [
                'dashboard_view', 'dashboard_edit',
                'orders_view', 'orders_edit',
                'users_view', 'users_edit',
                'teleconsultant_view'
            ],
        }
        
        # Assign permissions to roles
        for role_name, permission_codenames in role_permissions.items():
            try:
                role = Role.objects.get(name=role_name)
                # Clear existing permissions
                role.role_permissions.all().delete()
                
                # Add new permissions
                for codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        RolePermission.objects.create(
                            role=role,
                            permission=permission,
                            granted=True
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(f'Warning: Permission {codename} not found')
                
                self.stdout.write(f'Assigned {len(permission_codenames)} permissions to {role_name}')
                
            except Role.DoesNotExist:
                self.stdout.write(f'Warning: Role {role_name} not found')
        
        # Create a super admin user if none exists
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating super admin user...')
            superuser = User.objects.create_superuser(
                email='admin@atlas.com',
                password='admin123',
                full_name='Super Admin',
                phone_number='+1234567890'
            )
            
            # Assign Super Admin role
            super_admin_role = Role.objects.filter(name='Super Admin').first()
            if super_admin_role:
                UserRole.objects.create(
                    user=superuser,
                    role=super_admin_role,
                    is_primary=True,
                    is_active=True
                )
                self.stdout.write(f'Created super admin user: {superuser.email}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up permissions and roles!')
        ) 