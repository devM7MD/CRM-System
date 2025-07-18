from django.core.management.base import BaseCommand
from roles.models import Role

class Command(BaseCommand):
    help = 'Clean up roles to keep only Super Admin and Seller roles'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up roles...')
        
        # Get all roles except Super Admin and Seller
        roles_to_delete = Role.objects.exclude(name__in=['Super Admin', 'Seller'])
        
        if roles_to_delete.exists():
            self.stdout.write(f'Found {roles_to_delete.count()} roles to delete:')
            for role in roles_to_delete:
                self.stdout.write(f'  - {role.name}')
            
            # Delete the roles
            deleted_count = roles_to_delete.delete()[0]
            self.stdout.write(f'Deleted {deleted_count} roles.')
        else:
            self.stdout.write('No roles to delete.')
        
        # Ensure Super Admin and Seller roles are protected
        super_admin = Role.objects.filter(name='Super Admin').first()
        seller = Role.objects.filter(name='Seller').first()
        
        if super_admin:
            super_admin.is_protected = True
            super_admin.is_default = True
            super_admin.save()
            self.stdout.write('Updated Super Admin role as protected and default.')
        
        if seller:
            seller.is_protected = True
            seller.is_default = True
            seller.save()
            self.stdout.write('Updated Seller role as protected and default.')
        
        # Show final status
        remaining_roles = Role.objects.all()
        self.stdout.write(f'\nRemaining roles ({remaining_roles.count()}):')
        for role in remaining_roles:
            status = []
            if role.is_protected:
                status.append('Protected')
            if role.is_default:
                status.append('Default')
            status_str = ', '.join(status) if status else 'Custom'
            self.stdout.write(f'  - {role.name} ({status_str})')
        
        self.stdout.write(
            self.style.SUCCESS('Role cleanup completed successfully!')
        ) 