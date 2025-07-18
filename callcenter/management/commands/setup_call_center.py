from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils import timezone
from callcenter.models import (
    CallLog, AgentPerformance, AgentSession, CustomerInteraction,
    OrderStatusHistory, OrderAssignment, ManagerNote, TeamPerformance
)
from orders.models import Order
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up sample call center data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up call center data...')
        
        # Create groups if they don't exist
        agent_group, created = Group.objects.get_or_create(name='Call Center Agents')
        manager_group, created = Group.objects.get_or_create(name='Call Center Managers')
        
        # Create sample agents
        agents = []
        agent_data = [
            {'email': 'sarah.agent@example.com', 'full_name': 'Sarah Al-Mansouri', 'phone_number': '+971501234567'},
            {'email': 'ahmed.agent@example.com', 'full_name': 'Ahmed Khalil', 'phone_number': '+971502345678'},
            {'email': 'fatima.agent@example.com', 'full_name': 'Fatima Hassan', 'phone_number': '+971503456789'},
            {'email': 'omar.agent@example.com', 'full_name': 'Omar Rashid', 'phone_number': '+971504567890'},
        ]
        
        for data in agent_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'full_name': data['full_name'],
                    'phone_number': data['phone_number'],
                    'is_staff': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created agent: {user.get_full_name()}')
            user.groups.add(agent_group)
            agents.append(user)
        
        # Create sample managers
        managers = []
        manager_data = [
            {'email': 'ahmad.manager@example.com', 'full_name': 'Ahmad Al-Khalil', 'phone_number': '+971505678901'},
            {'email': 'nadia.manager@example.com', 'full_name': 'Nadia Mahmoud', 'phone_number': '+971506789012'},
        ]
        
        for data in manager_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'full_name': data['full_name'],
                    'phone_number': data['phone_number'],
                    'is_staff': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created manager: {user.get_full_name()}')
            user.groups.add(manager_group)
            managers.append(user)
        
        # Get or create some orders for assignment
        orders = Order.objects.all()[:20]  # Get first 20 orders
        
        if not orders.exists():
            self.stdout.write('No orders found. Please create some orders first.')
            return
        
        # Create sample assignments
        for order in orders:
            if not order.assignments.exists():
                agent = random.choice(agents)
                manager = random.choice(managers)
                priority = random.choice(['low', 'medium', 'high', 'urgent'])
                
                assignment = OrderAssignment.objects.create(
                    order=order,
                    manager=manager,
                    agent=agent,
                    priority_level=priority,
                    manager_notes=f'Sample assignment for testing. Priority: {priority}',
                )
                self.stdout.write(f'Assigned order {order.id} to {agent.get_full_name()}')
        
        # Create sample call logs
        call_statuses = ['completed', 'no_answer', 'busy', 'wrong_number', 'voicemail']
        for order in orders[:10]:  # Create call logs for first 10 orders
            if order.assignments.exists():
                agent = order.assignments.first().agent
                status = random.choice(call_statuses)
                duration = random.randint(30, 600)  # 30 seconds to 10 minutes
                
                call_log = CallLog.objects.create(
                    order=order,
                    agent=agent,
                    status=status,
                    duration=duration,
                    notes=f'Sample call log. Status: {status}, Duration: {duration}s',
                    customer_satisfaction=random.randint(1, 5) if status == 'completed' else None,
                    resolution_status='resolved' if status == 'completed' else 'pending',
                )
                self.stdout.write(f'Created call log for order {order.id}')
        
        # Create sample agent performance records
        today = timezone.now().date()
        for agent in agents:
            performance, created = AgentPerformance.objects.get_or_create(
                agent=agent,
                date=today,
                defaults={
                    'total_calls_made': random.randint(10, 50),
                    'successful_calls': random.randint(5, 30),
                    'orders_confirmed': random.randint(5, 25),
                    'orders_cancelled': random.randint(1, 10),
                    'orders_postponed': random.randint(1, 5),
                    'total_orders_handled': random.randint(15, 40),
                    'average_call_duration': round(random.uniform(2.0, 8.0), 2),
                    'resolution_rate': round(random.uniform(60.0, 95.0), 2),
                    'first_call_resolution_rate': round(random.uniform(50.0, 85.0), 2),
                    'customer_satisfaction_avg': round(random.uniform(3.5, 5.0), 2),
                    'total_work_time_minutes': random.randint(300, 480),  # 5-8 hours
                    'break_time_minutes': random.randint(30, 90),
                }
            )
            if created:
                self.stdout.write(f'Created performance record for {agent.get_full_name()}')
        
        # Create sample agent sessions
        for agent in agents:
            session, created = AgentSession.objects.get_or_create(
                agent=agent,
                defaults={
                    'status': random.choice(['available', 'busy', 'break']),
                    'concurrent_orders': random.randint(0, 5),
                    'workstation_id': f'WS-{random.randint(100, 999)}',
                }
            )
            if created:
                self.stdout.write(f'Created session for {agent.get_full_name()}')
        
        # Create sample manager notes
        for order in orders[:5]:
            if order.assignments.exists():
                assignment = order.assignments.first()
                note_types = ['instruction', 'reminder', 'priority', 'escalation']
                
                note = ManagerNote.objects.create(
                    order=order,
                    manager=assignment.manager,
                    agent=assignment.agent,
                    note_text=f'Sample manager note for order {order.id}. Please follow up with customer.',
                    note_type=random.choice(note_types),
                    is_urgent=random.choice([True, False]),
                )
                self.stdout.write(f'Created manager note for order {order.id}')
        
        # Create sample team performance
        team_performance, created = TeamPerformance.objects.get_or_create(
            team='Main Team',
            date=today,
            defaults={
                'total_agents': len(agents),
                'orders_handled': random.randint(50, 200),
                'orders_confirmed': random.randint(30, 150),
                'orders_cancelled': random.randint(5, 30),
                'average_handle_time': round(random.uniform(3.0, 8.0), 2),
                'team_confirmation_rate': round(random.uniform(70.0, 90.0), 2),
                'team_satisfaction_avg': round(random.uniform(4.0, 5.0), 2),
                'top_performer_agent': random.choice(agents),
                'lowest_performer_agent': random.choice(agents),
            }
        )
        if created:
            self.stdout.write('Created team performance record')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up call center data!')
        )
        self.stdout.write(f'Created {len(agents)} agents and {len(managers)} managers')
        self.stdout.write('Sample data includes:')
        self.stdout.write('- Order assignments')
        self.stdout.write('- Call logs')
        self.stdout.write('- Agent performance records')
        self.stdout.write('- Agent sessions')
        self.stdout.write('- Manager notes')
        self.stdout.write('- Team performance')
        self.stdout.write('\nYou can now test the call center system!') 