from django.core.management.base import BaseCommand
from users.models import User
from django.db import transaction, connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Force delete a user by ID or deleted email pattern'

    def add_arguments(self, parser):
        parser.add_argument('identifier', type=str, help='User ID or part of deleted email to match')
        parser.add_argument('--all-deleted', action='store_true', help='Delete all users with deleted_ in email')

    def handle(self, *args, **options):
        identifier = options['identifier']
        all_deleted = options['all_deleted']
        
        try:
            with transaction.atomic():
                if all_deleted:
                    # Find all users with 'deleted_' in their email
                    users = User.objects.filter(email__contains='deleted_')
                    count = users.count()
                    
                    if count == 0:
                        self.stdout.write(self.style.WARNING('No deleted users found'))
                        return
                    
                    self.stdout.write(self.style.WARNING(f'Found {count} deleted users. Deleting...'))
                    
                    # Get the user IDs
                    user_ids = list(users.values_list('id', flat=True))
                    
                    # Direct SQL to bypass ORM constraints
                    self._force_delete_users(user_ids)
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} users'))
                else:
                    # Try to find by ID first
                    try:
                        user = User.objects.get(id=identifier)
                        user_id = user.id
                    except (User.DoesNotExist, ValueError):
                        # If not found or not a valid ID, try by email pattern
                        users = User.objects.filter(email__contains=identifier)
                        if users.count() == 0:
                            self.stdout.write(self.style.ERROR(f'No user found with identifier: {identifier}'))
                            return
                        elif users.count() > 1:
                            self.stdout.write(self.style.WARNING(f'Found {users.count()} users matching {identifier}:'))
                            for user in users:
                                self.stdout.write(f'ID: {user.id}, Email: {user.email}')
                            return
                        user = users.first()
                        user_id = user.id
                    
                    self.stdout.write(self.style.WARNING(f'Deleting user: {user.id} - {user.email}'))
                    
                    # Force delete
                    self._force_delete_users([user_id])
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted user: {identifier}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting user(s): {str(e)}'))
    
    def _force_delete_users(self, user_ids):
        """Force delete users with direct SQL commands"""
        with connection.cursor() as cursor:
            # Delete related records in various tables
            tables_to_check = [
                # Format: (table_name, id_column)
                ('subscribers_subscriber', 'user_id'),
                ('users_auditlog', 'user_id'),
                ('users_userpermission', 'user_id'),
            ]
            
            # Check tables and delete related records
            for table, id_column in tables_to_check:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    for user_id in user_ids:
                        cursor.execute(f"DELETE FROM {table} WHERE {id_column} = ?", [user_id])
                        
            # Check for sourcing requests and other potential relationships
            potential_relations = [
                'sourcing_sourcingrequest',
                'orders_order',
                'callcenter_call',
                'delivery_delivery',
            ]
            
            for table in potential_relations:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    # Get column info to see if there's a user relationship
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    # Check for columns that might be related to users
                    for column in columns:
                        column_name = column[1]  # Column name is in position 1
                        if 'user_id' in column_name or 'seller_id' in column_name or 'agent_id' in column_name:
                            # Set NULL or delete based on the situation
                            for user_id in user_ids:
                                cursor.execute(f"UPDATE {table} SET {column_name} = NULL WHERE {column_name} = ?", [user_id])
            
            # Finally delete the users themselves
            for user_id in user_ids:
                cursor.execute("DELETE FROM users_user WHERE id = ?", [user_id])
                self.stdout.write(self.style.SUCCESS(f'Deleted user ID: {user_id}')) 