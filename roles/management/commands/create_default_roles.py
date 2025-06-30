from django.core.management.base import BaseCommand
from django.utils.text import slugify
from roles.models import Role, Permission

class Command(BaseCommand):
    help = 'Creates default roles and permissions for the system'

    def handle(self, *args, **options):
        self.stdout.write('Creating default permissions...')
        self.create_permissions()
        
        self.stdout.write('Creating default roles...')
        self.create_roles()
        
        self.stdout.write(self.style.SUCCESS('Successfully created default roles and permissions'))

    def create_permissions(self):
        # Dashboard permissions
        self._create_permission('View Dashboard', 'view_dashboard', 'dashboard', 'Can view dashboard statistics')
        self._create_permission('Manage Dashboard', 'manage_dashboard', 'dashboard', 'Can manage dashboard settings')
        
        # User permissions
        self._create_permission('View Users', 'view_users', 'users', 'Can view user list')
        self._create_permission('Add User', 'add_user', 'users', 'Can add new users')
        self._create_permission('Edit User', 'edit_user', 'users', 'Can edit user details')
        self._create_permission('Delete User', 'delete_user', 'users', 'Can delete users')
        
        # Seller permissions
        self._create_permission('View Sellers', 'view_sellers', 'sellers', 'Can view seller list')
        self._create_permission('Add Seller', 'add_seller', 'sellers', 'Can add new sellers')
        self._create_permission('Edit Seller', 'edit_seller', 'sellers', 'Can edit seller details')
        self._create_permission('Delete Seller', 'delete_seller', 'sellers', 'Can delete sellers')
        
        # Inventory permissions
        self._create_permission('View Inventory', 'view_inventory', 'inventory', 'Can view inventory')
        self._create_permission('Add Product', 'add_product', 'inventory', 'Can add new products')
        self._create_permission('Edit Product', 'edit_product', 'inventory', 'Can edit product details')
        self._create_permission('Delete Product', 'delete_product', 'inventory', 'Can delete products')
        
        # Order permissions
        self._create_permission('View Orders', 'view_orders', 'orders', 'Can view order list')
        self._create_permission('Add Order', 'add_order', 'orders', 'Can add new orders')
        self._create_permission('Edit Order', 'edit_order', 'orders', 'Can edit order details')
        self._create_permission('Delete Order', 'delete_order', 'orders', 'Can delete orders')
        
        # Call Center permissions
        self._create_permission('View Call Center', 'view_callcenter', 'callcenter', 'Can view call center dashboard')
        self._create_permission('Make Calls', 'make_calls', 'callcenter', 'Can make calls to customers')
        self._create_permission('View Call History', 'view_call_history', 'callcenter', 'Can view call history')
        
        # Packaging permissions
        self._create_permission('View Packaging', 'view_packaging', 'packaging', 'Can view packaging dashboard')
        self._create_permission('Package Orders', 'package_orders', 'packaging', 'Can package orders')
        
        # Delivery permissions
        self._create_permission('View Delivery', 'view_delivery', 'delivery', 'Can view delivery dashboard')
        self._create_permission('Assign Delivery', 'assign_delivery', 'delivery', 'Can assign deliveries to couriers')
        self._create_permission('Update Delivery Status', 'update_delivery_status', 'delivery', 'Can update delivery status')
        
        # Finance permissions
        self._create_permission('View Finance', 'view_finance', 'finance', 'Can view finance dashboard')
        self._create_permission('Add Payment', 'add_payment', 'finance', 'Can add payments')
        self._create_permission('Generate Invoice', 'generate_invoice', 'finance', 'Can generate invoices')
        
        # Warehouse permissions
        self._create_permission('View Warehouse', 'view_warehouse', 'warehouse', 'Can view warehouse dashboard')
        self._create_permission('Add to Warehouse', 'add_to_warehouse', 'warehouse', 'Can add items to warehouse')
        self._create_permission('Remove from Warehouse', 'remove_from_warehouse', 'warehouse', 'Can remove items from warehouse')
        
        # Settings permissions
        self._create_permission('View Settings', 'view_settings', 'settings', 'Can view system settings')
        self._create_permission('Edit Settings', 'edit_settings', 'settings', 'Can edit system settings')
        
        # Notification permissions
        self._create_permission('View Notifications', 'view_notifications', 'notifications', 'Can view notifications')
        self._create_permission('Mark Notifications as Read', 'mark_notifications_read', 'notifications', 'Can mark notifications as read')
        
        # Role permissions
        self._create_permission('View Roles', 'view_roles', 'roles', 'Can view roles')
        self._create_permission('Add Role', 'add_role', 'roles', 'Can add new roles')
        self._create_permission('Edit Role', 'edit_role', 'roles', 'Can edit role details')
        self._create_permission('Delete Role', 'delete_role', 'roles', 'Can delete roles')

    def create_roles(self):
        # Super Admin role
        super_admin = self._create_role(
            'Super Admin', 
            'Full access to all system features',
            is_system_role=True
        )
        
        # Add all permissions to Super Admin
        all_permissions = Permission.objects.all()
        super_admin.permissions.set(all_permissions)
        
        # Stock Keeper role
        stock_keeper = self._create_role(
            'Stock Keeper',
            'Manages inventory and warehouse operations',
            is_system_role=True,
            required_fields={
                'warehouse': True
            }
        )
        
        # Add Stock Keeper permissions
        stock_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_inventory',
                'add_product',
                'edit_product',
                'view_warehouse',
                'add_to_warehouse',
                'remove_from_warehouse',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        stock_keeper.permissions.set(stock_permissions)
        
        # Call Center Manager role
        call_center_manager = self._create_role(
            'Call Center Manager',
            'Manages call center operations and agents',
            is_system_role=True,
            required_fields={
                'call_center_team': True
            }
        )
        
        # Add Call Center Manager permissions
        cc_manager_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_callcenter',
                'make_calls',
                'view_call_history',
                'view_orders',
                'edit_order',
                'view_users',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        call_center_manager.permissions.set(cc_manager_permissions)
        
        # Call Center Agent role
        call_center_agent = self._create_role(
            'Call Center Agent',
            'Handles customer calls and support',
            is_system_role=True,
            required_fields={
                'call_center_team': True
            }
        )
        
        # Add Call Center Agent permissions
        cc_agent_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_callcenter',
                'make_calls',
                'view_call_history',
                'view_orders',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        call_center_agent.permissions.set(cc_agent_permissions)
        
        # Delivery role
        delivery = self._create_role(
            'Delivery',
            'Manages delivery operations',
            is_system_role=True,
            required_fields={
                'delivery_company': True
            }
        )
        
        # Add Delivery permissions
        delivery_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_delivery',
                'update_delivery_status',
                'view_orders',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        delivery.permissions.set(delivery_permissions)
        
        # Accountant role
        accountant = self._create_role(
            'Accountant',
            'Manages financial operations',
            is_system_role=True,
            required_fields={
                'accounting_department': True
            }
        )
        
        # Add Accountant permissions
        accountant_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_finance',
                'add_payment',
                'generate_invoice',
                'view_orders',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        accountant.permissions.set(accountant_permissions)
        
        # Seller role
        seller = self._create_role(
            'Seller',
            'Manages products and orders',
            is_system_role=True,
            required_fields={
                'company_name': True,
                'country': True,
                'expected_daily_orders': True
            }
        )
        
        # Add Seller permissions
        seller_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_inventory',
                'add_product',
                'edit_product',
                'view_orders',
                'add_order',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        seller.permissions.set(seller_permissions)
        
        # Packaging role
        packaging = self._create_role(
            'Packaging',
            'Handles order packaging',
            is_system_role=True
        )
        
        # Add Packaging permissions
        packaging_permissions = Permission.objects.filter(
            codename__in=[
                'view_dashboard',
                'view_packaging',
                'package_orders',
                'view_orders',
                'view_notifications',
                'mark_notifications_read'
            ]
        )
        packaging.permissions.set(packaging_permissions)

    def _create_permission(self, name, codename, category, description=''):
        """Helper method to create a permission if it doesn't exist."""
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            defaults={
                'name': name,
                'category': category,
                'description': description
            }
        )
        
        if created:
            self.stdout.write(f'Created permission: {name}')
        else:
            self.stdout.write(f'Permission already exists: {name}')
        
        return permission

    def _create_role(self, name, description='', is_system_role=False, required_fields=None):
        """Helper method to create a role if it doesn't exist."""
        if required_fields is None:
            required_fields = {}
            
        slug = slugify(name)
        
        role, created = Role.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'is_system_role': is_system_role,
                'required_fields': required_fields
            }
        )
        
        if created:
            self.stdout.write(f'Created role: {name}')
        else:
            self.stdout.write(f'Role already exists: {name}')
            
            # Update existing role
            role.name = name
            role.description = description
            role.is_system_role = is_system_role
            role.required_fields = required_fields
            role.save()
            
            self.stdout.write(f'Updated role: {name}')
        
        return role 