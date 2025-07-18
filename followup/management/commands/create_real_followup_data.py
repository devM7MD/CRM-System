from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random
from orders.models import Order
from users.models import User
from followup.models import FollowupRecord, CustomerFeedback


class Command(BaseCommand):
    help = 'Create real follow-up data from existing orders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of follow-up data',
        )

    def handle(self, *args, **options):
        if not options['force']:
            # Check if follow-up data already exists
            if FollowupRecord.objects.exists():
                self.stdout.write(
                    self.style.WARNING(
                        'Follow-up data already exists. Use --force to recreate.'
                    )
                )
                return

        self.stdout.write('Creating real follow-up data...')

        # Get all delivered orders
        delivered_orders = Order.objects.filter(status='delivered')
        
        if not delivered_orders.exists():
            self.stdout.write(
                self.style.WARNING('No delivered orders found. Creating sample follow-up data...')
            )
            # Create some sample data for testing
            self._create_sample_followup_data()
            return

        # Get available agents (users with staff status)
        agents = User.objects.filter(is_staff=True)
        if not agents.exists():
            self.stdout.write(
                self.style.WARNING('No staff users found. Using first user as agent.')
            )
            agents = User.objects.all()[:1]

        with transaction.atomic():
            # Clear existing data if force is used
            if options['force']:
                FollowupRecord.objects.all().delete()
                CustomerFeedback.objects.all().delete()
                self.stdout.write('Cleared existing follow-up data.')

            # Create follow-up records for delivered orders
            followup_records_created = 0
            feedback_created = 0

            for order in delivered_orders:
                # Create follow-up record
                agent = random.choice(agents)
                
                # Determine follow-up status based on order date
                days_since_delivery = (timezone.now().date() - order.date.date()).days
                
                if days_since_delivery < 3:
                    status = 'pending'
                    scheduled_for = order.date + timedelta(days=random.randint(3, 7))
                elif days_since_delivery < 7:
                    status = random.choice(['pending', 'in_progress'])
                    scheduled_for = order.date + timedelta(days=random.randint(3, 10))
                else:
                    status = random.choice(['completed', 'cancelled'])
                    scheduled_for = order.date + timedelta(days=random.randint(3, 14))

                # Create follow-up record
                followup_record = FollowupRecord.objects.create(
                    order=order,
                    agent=agent,
                    status=status,
                    scheduled_for=scheduled_for,
                    feedback='' if status == 'pending' else self._generate_feedback(status),
                    completed_at=timezone.now() if status == 'completed' else None,
                )
                followup_records_created += 1

                # Create customer feedback for completed follow-ups
                if status == 'completed':
                    feedback = CustomerFeedback.objects.create(
                        order=order,
                        rating=random.randint(3, 5),
                        comments=self._generate_feedback_comments(),
                    )
                    feedback_created += 1

            # Create some pending follow-ups for orders in delivery
            in_delivery_orders = Order.objects.filter(status='in_delivery')
            for order in in_delivery_orders[:5]:  # Limit to 5
                agent = random.choice(agents)
                scheduled_for = timezone.now() + timedelta(days=random.randint(1, 5))
                
                FollowupRecord.objects.create(
                    order=order,
                    agent=agent,
                    status='pending',
                    scheduled_for=scheduled_for,
                )
                followup_records_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {followup_records_created} follow-up records and {feedback_created} feedback records.'
                )
            )

    def _create_sample_followup_data(self):
        """Create sample follow-up data when no delivered orders exist."""
        # Get or create a sample agent
        agent, created = User.objects.get_or_create(
            username='followup_agent',
            defaults={
                'first_name': 'Follow-up',
                'last_name': 'Agent',
                'email': 'followup@example.com',
                'is_staff': True,
            }
        )

        # Create sample follow-up records
        sample_orders = [
            {'order_code': 'ORD-001', 'customer_name': 'John Smith', 'status': 'delivered'},
            {'order_code': 'ORD-002', 'customer_name': 'Jane Doe', 'status': 'delivered'},
            {'order_code': 'ORD-003', 'customer_name': 'Mike Johnson', 'status': 'in_delivery'},
        ]

        for i, order_data in enumerate(sample_orders):
            # Create sample order if it doesn't exist
            order, created = Order.objects.get_or_create(
                order_code=order_data['order_code'],
                defaults={
                    'customer_name': order_data['customer_name'],
                    'customer_phone': f'+1234567890{i}',
                    'status': order_data['status'],
                    'date': timezone.now() - timedelta(days=random.randint(1, 30)),
                }
            )

            # Create follow-up record
            status = random.choice(['pending', 'in_progress', 'completed'])
            scheduled_for = timezone.now() + timedelta(days=random.randint(1, 7))
            
            followup_record = FollowupRecord.objects.create(
                order=order,
                agent=agent,
                status=status,
                scheduled_for=scheduled_for,
                feedback='Sample follow-up feedback' if status != 'pending' else '',
                completed_at=timezone.now() if status == 'completed' else None,
            )

            # Create feedback for completed follow-ups
            if status == 'completed':
                CustomerFeedback.objects.create(
                    order=order,
                    rating=random.randint(3, 5),
                    comments='Sample customer feedback comment.',
                )

        self.stdout.write(
            self.style.SUCCESS('Created sample follow-up data for testing.')
        )

    def _generate_feedback(self, status):
        """Generate realistic follow-up feedback."""
        feedback_templates = {
            'completed': [
                'Customer satisfied with delivery. No issues reported.',
                'Follow-up call completed successfully. Customer happy with service.',
                'Product received in good condition. Customer provided positive feedback.',
                'Delivery completed as expected. Customer confirmed satisfaction.',
            ],
            'in_progress': [
                'Attempted to contact customer. Will try again tomorrow.',
                'Left voicemail message. Awaiting customer response.',
                'Customer requested callback later. Scheduled for follow-up.',
                'Initial contact made. Customer has some questions.',
            ],
            'cancelled': [
                'Customer requested to cancel follow-up.',
                'Unable to reach customer after multiple attempts.',
                'Follow-up cancelled due to customer unavailability.',
                'Customer declined follow-up service.',
            ]
        }
        return random.choice(feedback_templates.get(status, ['Follow-up in progress.']))

    def _generate_feedback_comments(self):
        """Generate realistic customer feedback comments."""
        comments = [
            'Great service and fast delivery!',
            'Product quality exceeded expectations.',
            'Very satisfied with the overall experience.',
            'Good communication throughout the process.',
            'Would definitely recommend to others.',
            'Professional service and timely delivery.',
            'Product arrived in perfect condition.',
            'Excellent customer support team.',
        ]
        return random.choice(comments) 