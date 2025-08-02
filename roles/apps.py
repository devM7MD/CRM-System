from django.apps import AppConfig


class RolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'roles'

    def ready(self):
        """Create build-in roles when the app is ready"""
        try:
            from .models import Role
            
            # Build-in roles that should always exist
            build_in_roles = [
                {
                    'name': 'Admin',
                    'description': 'System administrator with full access',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Call Center Agent',
                    'description': 'Handles customer calls and order processing',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Call Center Manager',
                    'description': 'Manages call center operations and team',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Accountant',
                    'description': 'Manages financial operations and reports',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Stock Keeper',
                    'description': 'Manages inventory and stock operations',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Delivery Agent',
                    'description': 'Handles delivery operations and tracking',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Packaging Agent',
                    'description': 'Handles packaging and preparation',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Sourcing Agent',
                    'description': 'Handles product sourcing and supplier management',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Seller',
                    'description': 'External seller with limited access',
                    'is_protected': True,
                    'is_default': False,
                },
                {
                    'name': 'Follow-up Agent',
                    'description': 'Handles customer follow-up and support',
                    'is_protected': True,
                    'is_default': False,
                },
            ]
            
            # Create build-in roles if they don't exist
            for role_data in build_in_roles:
                Role.objects.get_or_create(
                    name=role_data['name'],
                    defaults=role_data
                )
                
        except Exception as e:
            # Ignore errors during migration
            pass
