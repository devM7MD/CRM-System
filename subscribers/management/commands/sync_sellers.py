from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from subscribers.models import Subscriber

User = get_user_model()

class Command(BaseCommand):
    help = 'Sync existing sellers with subscribers table'

    def handle(self, *args, **options):
        # Get all users with seller role
        sellers = User.objects.filter(role='seller', is_active=True)
        synced_count = 0

        for seller in sellers:
            subscriber, created = Subscriber.objects.get_or_create(
                user=seller,
                defaults={
                    'full_name': seller.full_name,
                    'email': seller.email,
                    'phone_number': seller.phone_number,
                    'business_name': seller.company_name or seller.full_name,
                    'residence_country': seller.country,  # country is already a string
                    'store_link': '',  # Will be updated if seller has a store link
                    'services': ['Seller']  # Default service
                }
            )
            if created:
                synced_count += 1
                self.stdout.write(f'Created subscriber for {seller.full_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced {synced_count} sellers to subscribers'
            )
        ) 