from django.core.management.base import BaseCommand
from orders.models import Order
from products.models import Product
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample orders with the new model structure'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample orders...')
        
        # Get or create some products
        products = list(Product.objects.all())
        if not products:
            self.stdout.write('No products found. Please create some products first.')
            return
        
        # Sample seller emails (since we don't have users yet)
        seller_emails = [
            'seller1@atlas.com',
            'seller2@atlas.com',
            'seller3@atlas.com',
            'seller4@atlas.com',
            'seller5@atlas.com'
        ]
        
        # Sample customer data
        customers = [
            'Ahmed Al Mansouri',
            'Fatima Al Zahra',
            'Omar Al Rashid',
            'Khalid Al Qasimi',
            'Aisha Al Falasi',
            'Mohammed Al Suwaidi',
            'Layla Al Maktoum',
            'Youssef Al Nahyan',
            'Noor Al Qassimi',
            'Hassan Al Sharqi'
        ]
        
        # Sample phone numbers
        phone_numbers = [
            '+971501234567',
            '+971502345678',
            '+971503456789',
            '+971504567890',
            '+971505678901',
            '+971506789012',
            '+971507890123',
            '+971508901234',
            '+971509012345',
            '+971500123456'
        ]
        
        # Sample addresses
        addresses = [
            '123 Sheikh Zayed Road, Dubai',
            '456 Al Wasl Road, Dubai',
            '789 Jumeirah Beach Road, Dubai',
            '321 Al Khaleej Street, Abu Dhabi',
            '654 Corniche Road, Abu Dhabi',
            '987 Al Ain Road, Al Ain',
            '147 Al Majaz Street, Sharjah',
            '258 Al Qasba, Sharjah',
            '369 Al Mamzar, Dubai',
            '741 Al Barsha, Dubai'
        ]
        
        # Sample store links
        store_links = [
            'https://shop.example.com',
            'https://store.atlas.com',
            'https://marketplace.ae',
            'https://online-shop.ae',
            'https://ecommerce.ae'
        ]
        
        # Status choices
        statuses = ['pending', 'processing', 'confirmed', 'shipped', 'delivered']
        
        # Create sample orders
        orders_created = 0
        for i in range(50):  # Create 50 sample orders
            # Random date within last 30 days
            random_days = random.randint(0, 30)
            order_date = timezone.now() - timedelta(days=random_days)
            
            # Random customer and phone
            customer = random.choice(customers)
            phone = random.choice(phone_numbers)
            
            # Random product and quantity
            product = random.choice(products)
            quantity = random.randint(1, 5)
            
            # Random price in AED (reasonable range)
            price_per_unit = round(random.uniform(50.0, 2000.0), 2)
            
            # Random seller email
            seller_email = random.choice(seller_emails)
            
            # Random status (weighted towards pending and processing)
            status = random.choices(
                statuses, 
                weights=[0.3, 0.3, 0.2, 0.15, 0.05]
            )[0]
            
            # Random address
            address = random.choice(addresses)
            city = 'Dubai' if 'Dubai' in address else 'Abu Dhabi' if 'Abu Dhabi' in address else 'Sharjah'
            state = 'Dubai' if 'Dubai' in address else 'Abu Dhabi' if 'Abu Dhabi' in address else 'Sharjah'
            zip_code = f"{random.randint(10000, 99999)}"
            country = 'UAE'
            
            # Random store link
            store_link = random.choice(store_links)
            
            # Random notes
            notes = random.choice([
                'Handle with care',
                'Gift wrap requested',
                'Delivery before 2 PM',
                'Leave at reception',
                'Call before delivery',
                'Signature required',
                'Fragile items',
                'Express delivery',
                '',
                ''
            ])
            
            # Create the order
            order = Order.objects.create(
                customer=customer,
                date=order_date,
                product=product,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=status,
                customer_phone=phone,
                seller_email=seller_email,
                store_link=store_link,
                shipping_address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                country=country,
                notes=notes,
                internal_notes=f'Sample order {i+1} created for testing purposes.'
            )
            
            orders_created += 1
            if orders_created % 10 == 0:
                self.stdout.write(f'Created {orders_created} orders...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {orders_created} sample orders!')
        ) 