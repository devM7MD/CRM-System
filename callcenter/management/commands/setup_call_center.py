from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from callcenter.models import (
    CallCenterAgent, AgentSession, CallLog, CustomerInteraction,
    OrderAssignment, ManagerNote, OrderStatusHistory, AgentPerformance, TeamPerformance
)
from orders.models import Order
from roles.models import Role, Permission, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up call center system with roles, permissions, and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Call Center System...'))
        
        # Create roles and permissions
        self.create_roles_and_permissions()
        
        # Create sample users
        self.create_sample_users()
        
        # Create agent profiles
        self.create_agent_profiles()
        
        # Create sample data
        self.create_sample_data()
        
        self.stdout.write(self.style.SUCCESS('Call Center System setup completed successfully!'))

    def create_roles_and_permissions(self):
        """Create call center roles and permissions"""
        self.stdout.write('Creating roles and permissions...')
        
        # Create permissions for call center module
        permissions_data = [
            {
                'name': 'View Call Center Dashboard',
                'codename': 'view_call_center_dashboard',
                'permission_type': 'read',
                'module': 'callcenter',
                'description': 'Permission to view call center dashboard'
            },
            {
                'name': 'Manage Orders',
                'codename': 'manage_orders',
                'permission_type': 'update',
                'module': 'callcenter',
                'description': 'Permission to manage orders in call center'
            },
            {
                'name': 'Assign Orders',
                'codename': 'assign_orders',
                'permission_type': 'create',
                'module': 'callcenter',
                'description': 'Permission to assign orders to agents'
            },
            {
                'name': 'View Agent Reports',
                'codename': 'view_agent_reports',
                'permission_type': 'read',
                'module': 'callcenter',
                'description': 'Permission to view agent performance reports'
            },
            {
                'name': 'Create Manager Notes',
                'codename': 'create_manager_notes',
                'permission_type': 'create',
                'module': 'callcenter',
                'description': 'Permission to create notes for agents'
            },
            {
                'name': 'Log Calls',
                'codename': 'log_calls',
                'permission_type': 'create',
                'module': 'callcenter',
                'description': 'Permission to log customer calls'
            },
            {
                'name': 'Update Order Status',
                'codename': 'update_order_status',
                'permission_type': 'update',
                'module': 'callcenter',
                'description': 'Permission to update order status'
            },
            {
                'name': 'View Customer Interactions',
                'codename': 'view_customer_interactions',
                'permission_type': 'read',
                'module': 'callcenter',
                'description': 'Permission to view customer interactions'
            },
            {
                'name': 'Manage Agent Availability',
                'codename': 'manage_agent_availability',
                'permission_type': 'update',
                'module': 'callcenter',
                'description': 'Permission to manage agent availability status'
            },
        ]
        
        created_permissions = []
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                permission_type=perm_data['permission_type'],
                module=perm_data['module'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description'],
                }
            )
            created_permissions.append(perm)
            if created:
                self.stdout.write(f'  Created permission: {perm_data["name"]}')
        
        # Create Call Center Manager role
        manager_role, created = Role.objects.get_or_create(
            name='Call Center Manager',
            defaults={
                'role_type': 'callcenter_manager',
                'description': 'Manages call center operations and assigns orders to agents',
                'is_active': True
            }
        )
        if created:
            # Add all permissions to manager role
            for perm in created_permissions:
                manager_role.role_permissions.create(permission=perm, granted=True)
            self.stdout.write('  Created Call Center Manager role')
        
        # Create Call Center Agent role
        agent_role, created = Role.objects.get_or_create(
            name='Call Center Agent',
            defaults={
                'role_type': 'teleconsultant',
                'description': 'Handles customer calls and manages assigned orders',
                'is_active': True
            }
        )
        if created:
            # Agents get limited permissions
            agent_permission_codenames = [
                'view_call_center_dashboard',
                'log_calls',
                'update_order_status',
                'view_customer_interactions',
                'manage_agent_availability',
            ]
            agent_perms = [p for p in created_permissions if p.codename in agent_permission_codenames]
            for perm in agent_perms:
                agent_role.role_permissions.create(permission=perm, granted=True)
            self.stdout.write('  Created Call Center Agent role')

    def create_sample_users(self):
        """Create sample call center users"""
        self.stdout.write('Creating sample users...')
        
        # Get roles
        manager_role = Role.objects.get(name='Call Center Manager')
        agent_role = Role.objects.get(name='Call Center Agent')
        
        # Create manager
        manager, created = User.objects.get_or_create(
            email='manager@callcenter.com',
            defaults={
                'full_name': 'Ahmad Al-Khalil',
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            self.stdout.write('  Created Call Center Manager: manager@callcenter.com (password: manager123)')
        # Assign manager role as primary
        UserRole.objects.get_or_create(
            user=manager,
            role=manager_role,
            defaults={
                'is_primary': True,
                'is_active': True,
            }
        )
        
        # Create agents
        agents_data = [
            {
                'email': 'sarah@callcenter.com',
                'full_name': 'Sarah Al-Mansouri',
                'employee_id': 'CC001',
                'team': 'Team Alpha',
            },
            {
                'email': 'omar@callcenter.com',
                'full_name': 'Omar Al-Rashid',
                'employee_id': 'CC002',
                'team': 'Team Alpha',
            },
            {
                'email': 'fatima@callcenter.com',
                'full_name': 'Fatima Al-Zahra',
                'employee_id': 'CC003',
                'team': 'Team Beta',
            },
            {
                'email': 'khalid@callcenter.com',
                'full_name': 'Khalid Al-Maktoum',
                'employee_id': 'CC004',
                'team': 'Team Beta',
            },
        ]
        
        created_agents = []
        for agent_data in agents_data:
            user, created = User.objects.get_or_create(
                email=agent_data['email'],
                defaults={
                    'full_name': agent_data['full_name'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('agent123')
                user.save()
                self.stdout.write(f'  Created Agent: {agent_data["email"]} (password: agent123)')
            # Assign agent role as primary
            UserRole.objects.get_or_create(
                user=user,
                role=agent_role,
                defaults={
                    'is_primary': True,
                    'is_active': True,
                }
            )
            created_agents.append((user, agent_data))
        
        return manager, created_agents

    def create_agent_profiles(self):
        """Create call center agent profiles"""
        self.stdout.write('Creating agent profiles...')
        
        # Get manager
        manager = User.objects.get(email='manager@callcenter.com')
        agent_role = Role.objects.get(name='Call Center Agent')
        
        # Create profiles for all users who have a primary UserRole as Call Center Agent
        agents = User.objects.filter(user_roles__role=agent_role, user_roles__is_primary=True)
        
        for agent in agents:
            profile, created = CallCenterAgent.objects.get_or_create(
                user=agent,
                defaults={
                    'employee_id': f'CC{agent.id:03d}',
                    'phone_extension': f'2{agent.id:03d}',
                    'status': 'active',
                    'availability': random.choice(['available', 'busy', 'break']),
                    'supervisor': manager,
                    'team': random.choice(['Team Alpha', 'Team Beta']),
                    'skills': ['customer_service', 'order_management', 'problem_solving'],
                }
            )
            if created:
                self.stdout.write(f'  Created profile for {agent.get_full_name()}')

    def create_sample_data(self):
        """Create sample call center data"""
        self.stdout.write('Creating sample data...')
        
        # Get users
        manager = User.objects.get(email='manager@callcenter.com')
        agents = User.objects.filter(primary_role__name='Call Center Agent')
        orders = Order.objects.all()[:20]  # Get first 20 orders
        
        if not orders.exists():
            self.stdout.write(self.style.WARNING('  No orders found. Please create some orders first.'))
            return
        
        # Create order assignments
        for order in orders:
            agent = random.choice(agents)
            assignment, created = OrderAssignment.objects.get_or_create(
                order=order,
                assigned_agent=agent,
                defaults={
                    'assigned_by': manager,
                    'priority': random.choice(['low', 'medium', 'high', 'urgent']),
                    'expected_completion': timezone.now() + timedelta(hours=random.randint(1, 24)),
                    'assignment_notes': random.choice([
                        'Customer requested callback',
                        'High priority order',
                        'Follow up required',
                        'Standard processing',
                        'Customer has questions'
                    ]),
                }
            )
        
        # Create call logs
        for order in orders[:10]:  # Create calls for first 10 orders
            agent = random.choice(agents)
            call_status = random.choice(['completed', 'no_answer', 'busy', 'wrong_number'])
            
            call_log = CallLog.objects.create(
                order=order,
                agent=agent,
                duration=random.randint(30, 600),  # 30 seconds to 10 minutes
                status=call_status,
                notes=random.choice([
                    'Customer confirmed order',
                    'Customer requested changes',
                    'No answer - will try again',
                    'Customer busy - scheduled callback',
                    'Wrong number provided'
                ]),
                customer_satisfaction=random.randint(1, 5) if call_status == 'completed' else None,
            )
        
        # Create customer interactions
        for order in orders[:5]:
            agent = random.choice(agents)
            CustomerInteraction.objects.create(
                order=order,
                agent=agent,
                interaction_type=random.choice(['call', 'email', 'follow_up']),
                duration_minutes=random.randint(2, 15),
                resolution_status=random.choice(['resolved', 'pending', 'follow_up_required']),
                interaction_notes='Sample interaction for demonstration',
                customer_satisfaction=random.randint(1, 5),
            )
        
        # Create manager notes
        for order in orders[:3]:
            agent = random.choice(agents)
            ManagerNote.objects.create(
                order=order,
                manager=manager,
                agent=agent,
                note_text=random.choice([
                    'Please follow up with customer regarding delivery time',
                    'Customer has special requirements - handle with care',
                    'High priority customer - ensure excellent service',
                    'Customer requested specific delivery instructions',
                    'Previous order was cancelled - check customer satisfaction'
                ]),
                note_type=random.choice(['instruction', 'reminder', 'priority']),
                is_urgent=random.choice([True, False]),
            )
        
        # Create agent performance records
        today = timezone.now().date()
        for agent in agents:
            performance, created = AgentPerformance.objects.get_or_create(
                agent=agent,
                date=today,
                defaults={
                    'total_orders_handled': random.randint(5, 25),
                    'orders_confirmed': random.randint(3, 20),
                    'orders_cancelled': random.randint(0, 3),
                    'orders_postponed': random.randint(0, 2),
                    'total_calls_made': random.randint(10, 50),
                    'successful_calls': random.randint(8, 45),
                    'average_call_duration': round(random.uniform(2.0, 8.0), 2),
                    'customer_satisfaction_avg': round(random.uniform(3.5, 5.0), 2),
                    'resolution_rate': round(random.uniform(70.0, 95.0), 2),
                    'first_call_resolution_rate': round(random.uniform(60.0, 85.0), 2),
                    'total_work_time_minutes': random.randint(360, 480),  # 6-8 hours
                    'break_time_minutes': random.randint(30, 60),
                }
            )
        
        # Create team performance
        teams = ['Team Alpha', 'Team Beta']
        for team in teams:
            team_performance, created = TeamPerformance.objects.get_or_create(
                team_name=team,
                date=today,
                defaults={
                    'total_agents': random.randint(2, 4),
                    'active_agents': random.randint(1, 3),
                    'total_orders_handled': random.randint(20, 50),
                    'orders_confirmed': random.randint(15, 40),
                    'orders_cancelled': random.randint(1, 5),
                    'average_handle_time': round(random.uniform(3.0, 7.0), 2),
                    'team_confirmation_rate': round(random.uniform(75.0, 90.0), 2),
                    'team_satisfaction_avg': round(random.uniform(4.0, 5.0), 2),
                    'top_performer_agent': random.choice(agents),
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created sample data for {orders.count()} orders'))
        self.stdout.write(self.style.SUCCESS('  Created call logs, interactions, notes, and performance records')) 