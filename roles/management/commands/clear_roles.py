from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from roles.models import Role, Permission, RolePermission, UserRole
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Clear all default roles and make the role system dynamic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL roles, permissions, and user role assignments. '
                    'This action cannot be undone!\n'
                    'Use --force to proceed.'
                )
            )
            return

        with transaction.atomic():
            self.stdout.write('Clearing all roles and permissions...')
            
            # Delete all user role assignments
            user_role_count = UserRole.objects.count()
            UserRole.objects.all().delete()
            self.stdout.write(f'Deleted {user_role_count} user role assignments')
            
            # Delete all role permissions
            role_permission_count = RolePermission.objects.count()
            RolePermission.objects.all().delete()
            self.stdout.write(f'Deleted {role_permission_count} role permissions')
            
            # Delete all roles
            role_count = Role.objects.count()
            Role.objects.all().delete()
            self.stdout.write(f'Deleted {role_count} roles')
            
            # Delete all permissions
            permission_count = Permission.objects.count()
            Permission.objects.all().delete()
            self.stdout.write(f'Deleted {permission_count} permissions')
            
            # Create a basic "Admin" role for the superuser
            admin_role = Role.objects.create(
                name='Admin',
                role_type='admin',
                description='Basic administrator role',
                is_active=True,
                is_default=False,
            )
            
            # Create basic permissions
            basic_permissions = [
                {'name': 'View Dashboard', 'codename': 'view_dashboard', 'permission_type': 'read', 'module': 'dashboard'},
                {'name': 'View Users', 'codename': 'view_users', 'permission_type': 'read', 'module': 'users'},
                {'name': 'Create Users', 'codename': 'create_users', 'permission_type': 'create', 'module': 'users'},
                {'name': 'Edit Users', 'codename': 'edit_users', 'permission_type': 'update', 'module': 'users'},
                {'name': 'Delete Users', 'codename': 'delete_users', 'permission_type': 'delete', 'module': 'users'},
                {'name': 'View Roles', 'codename': 'view_roles', 'permission_type': 'read', 'module': 'roles'},
                {'name': 'Create Roles', 'codename': 'create_roles', 'permission_type': 'create', 'module': 'roles'},
                {'name': 'Edit Roles', 'codename': 'edit_roles', 'permission_type': 'update', 'module': 'roles'},
                {'name': 'Delete Roles', 'codename': 'delete_roles', 'permission_type': 'delete', 'module': 'roles'},
            ]
            
            created_permissions = []
            for perm_data in basic_permissions:
                permission = Permission.objects.create(**perm_data)
                created_permissions.append(permission)
                self.stdout.write(f'Created permission: {permission.name}')
            
            # Assign all permissions to admin role
            for permission in created_permissions:
                RolePermission.objects.create(
                    role=admin_role,
                    permission=permission,
                    granted=True
                )
            
            self.stdout.write(f'Assigned {len(created_permissions)} permissions to Admin role')
            
            # Assign admin role to existing superusers
            superusers = User.objects.filter(is_superuser=True)
            for user in superusers:
                UserRole.objects.create(
                    user=user,
                    role=admin_role,
                    is_primary=True,
                    is_active=True
                )
                self.stdout.write(f'Assigned Admin role to superuser: {user.email}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully cleared all default roles and created a dynamic role system!\n'
                    'You can now create custom roles through the admin interface.'
                )
            ) 