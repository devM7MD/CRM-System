from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from callcenter.models import AgentSession, AgentPerformance, OrderAssignment, CallLog
from orders.models import Order
from roles.models import Role, UserRole
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up real call center data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up call center data...')
        
        # Get or create Call Center roles
        call_center_agent_role, created = Role.objects.get_or_create(
            name='Call Center Agent',
            defaults={'description': 'Call center agent role'}
        )
        
        call_center_manager_role, created = Role.objects.get_or_create(
            name='Call Center Manager',
            defaults={'description': 'Call center manager role'}
        )
        
        # Create call center agents
        agents_data = [
            {'email': 'sarah.agent@atlas.com', 'full_name': 'Sarah Al-Mansouri', 'phone_number': '+971-50-111-1111'},
            {'email': 'omar.agent@atlas.com', 'full_name': 'Omar Al-Rashid', 'phone_number': '+971-50-222-2222'},
            {'email': 'fatima.agent@atlas.com', 'full_name': 'Fatima Hassan', 'phone_number': '+971-50-333-3333'},
            {'email': 'ahmed.agent@atlas.com', 'full_name': 'Ahmed Al-Zahra', 'phone_number': '+971-50-444-4444'},
            {'email': 'layla.agent@atlas.com', 'full_name': 'Layla Al-Amiri', 'phone_number': '+971-50-555-5555'},
        ]
        
        agents = []
        for agent_data in agents_data:
            user, created = User.objects.get_or_create(
                email=agent_data['email'],
                defaults={
                    'full_name': agent_data['full_name'],
                    'phone_number': agent_data['phone_number'],
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Assign Call Center Agent role
                UserRole.objects.get_or_create(
                    user=user,
                    role=call_center_agent_role,
                    defaults={'is_primary': True, 'is_active': True}
                )
                
                self.stdout.write(f'Created agent: {user.full_name}')
            
            agents.append(user)
        
        # Create call center manager
        manager, created = User.objects.get_or_create(
            email='manager@atlas.com',
            defaults={
                'full_name': 'Mohamed Abbas',
                'phone_number': '+971-50-999-9999',
                'is_active': True,
            }
        )
        
        if created:
            manager.set_password('password123')
            manager.save()
            
            # Assign Call Center Manager role
            UserRole.objects.get_or_create(
                user=manager,
                role=call_center_manager_role,
                defaults={'is_primary': True, 'is_active': True}
            )
            
            self.stdout.write(f'Created manager: {manager.full_name}')
        
        # Create agent sessions
        today = timezone.now().date()
        session_statuses = ['available', 'busy', 'break', 'offline']
        
        for agent in agents:
            # Create today's session
            session, created = AgentSession.objects.get_or_create(
                agent=agent,
                defaults={
                    'status': random.choice(session_statuses),
                    'concurrent_orders': random.randint(0, 5),
                }
            )
            
            if created:
                self.stdout.write(f'Created session for {agent.full_name}')
        
        # Create performance records for the last 7 days
        for i in range(7):
            date = today - timedelta(days=i)
            
            for agent in agents:
                performance, created = AgentPerformance.objects.get_or_create(
                    agent=agent,
                    date=date,
                    defaults={
                        'total_calls_made': random.randint(15, 30),
                        'successful_calls': random.randint(12, 25),
                        'orders_confirmed': random.randint(10, 20),
                        'orders_cancelled': random.randint(1, 5),
                        'orders_postponed': random.randint(1, 3),
                        'total_orders_handled': random.randint(15, 25),
                        'average_call_duration': round(random.uniform(2.5, 5.0), 1),
                        'resolution_rate': round(random.uniform(75.0, 95.0), 1),
                        'first_call_resolution_rate': round(random.uniform(80.0, 95.0), 1),
                        'customer_satisfaction_avg': round(random.uniform(3.5, 5.0), 1),
                        'total_work_time_minutes': random.randint(300, 480),
                        'break_time_minutes': random.randint(30, 60),
                    }
                )
                
                if created:
                    self.stdout.write(f'Created performance record for {agent.full_name} on {date}')
        
        # Create some order assignments
        orders = Order.objects.all()[:20]  # Get first 20 orders
        
        for order in orders:
            if not order.assignments.exists():
                agent = random.choice(agents)
                assignment = OrderAssignment.objects.create(
                    order=order,
                    manager=manager,
                    agent=agent,
                    priority_level=random.choice(['low', 'medium', 'high', 'urgent']),
                    manager_notes=f'Assigned to {agent.full_name} for processing',
                    assignment_date=timezone.now() - timedelta(hours=random.randint(1, 24))
                )
                
                self.stdout.write(f'Assigned order {order.id} to {agent.full_name}')
        
        # Create some call logs
        for order in orders[:10]:  # Create call logs for first 10 orders
            if order.assignments.exists():
                agent = order.assignments.first().agent
                
                call_log = CallLog.objects.create(
                    order=order,
                    agent=agent,
                    duration=random.randint(60, 300),  # 1-5 minutes
                    status=random.choice(['completed', 'no_answer', 'busy', 'voicemail']),
                    notes=f'Call made to customer for order {order.id}',
                    customer_satisfaction=random.randint(3, 5) if random.random() > 0.3 else None,
                    resolution_status='resolved' if random.random() > 0.2 else 'pending'
                )
                
                self.stdout.write(f'Created call log for order {order.id}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up call center data:\n'
                f'- {len(agents)} agents created\n'
                f'- 1 manager created\n'
                f'- Agent sessions created\n'
                f'- Performance records created for last 7 days\n'
                f'- Order assignments created\n'
                f'- Call logs created'
            )
        ) 