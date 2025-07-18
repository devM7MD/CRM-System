from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from sourcing.models import Supplier, SourcingRequest
from sellers.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Create real sourcing data from existing orders and materials'

    def handle(self, *args, **options):
        self.stdout.write('Creating real sourcing data...')
        
        # Create some sample products if they don't exist
        products_data = [
            {
                'name_en': 'iPhone 15 Pro Max',
                'name_ar': 'آيفون 15 برو ماكس',
                'code': 'IPH15PM',
                'description': 'Latest iPhone with titanium design and advanced camera system',
                'selling_price': 4999.00,
                'purchase_price': 3500.00,
            },
            {
                'name_en': 'Samsung Galaxy S24 Ultra',
                'name_ar': 'سامسونج جالكسي إس 24 الترا',
                'code': 'SGS24U',
                'description': 'Premium Android smartphone with S Pen and AI features',
                'selling_price': 4499.00,
                'purchase_price': 3200.00,
            },
            {
                'name_en': 'MacBook Pro 16" M3',
                'name_ar': 'ماك بوك برو 16 بوصة إم 3',
                'code': 'MBP16M3',
                'description': 'Professional laptop with M3 chip for power users',
                'selling_price': 8999.00,
                'purchase_price': 6500.00,
            },
            {
                'name_en': 'iPad Pro 12.9"',
                'name_ar': 'آيباد برو 12.9 بوصة',
                'code': 'IPADP12',
                'description': 'Professional tablet with M2 chip and Apple Pencil support',
                'selling_price': 3999.00,
                'purchase_price': 2800.00,
            },
            {
                'name_en': 'AirPods Pro 2nd Gen',
                'name_ar': 'إيربودز برو الجيل الثاني',
                'code': 'APP2',
                'description': 'Wireless earbuds with active noise cancellation',
                'selling_price': 999.00,
                'purchase_price': 600.00,
            },
        ]
        
        # Create products
        products = []
        users = User.objects.filter(is_staff=True)
        if not users.exists():
            self.stdout.write(self.style.ERROR('No staff users found. Please create users first.'))
            return
        
        for product_data in products_data:
            # Assign a seller to the product
            seller = random.choice(users)
            product_data['seller'] = seller
            
            product, created = Product.objects.get_or_create(
                code=product_data['code'],
                defaults=product_data
            )
            products.append(product)
        
        # Create suppliers
        suppliers_data = [
            {
                'name': 'TechSource Global',
                'contact_person': 'Ahmed Hassan',
                'email': 'ahmed@techsource.com',
                'phone': '+971501234567',
                'country': 'UAE',
                'category': 'Electronics',
                'quality_score': 4.5,
                'delivery_score': 4.3,
                'price_score': 4.2,
                'total_orders': 150,
                'is_active': True,
            },
            {
                'name': 'Mobile World Suppliers',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@mobileworld.com',
                'phone': '+971502345678',
                'country': 'China',
                'category': 'Mobile Devices',
                'quality_score': 4.2,
                'delivery_score': 4.0,
                'price_score': 4.5,
                'total_orders': 89,
                'is_active': True,
            },
            {
                'name': 'Gadget Pro International',
                'contact_person': 'Mohammed Ali',
                'email': 'mohammed@gadgetpro.com',
                'phone': '+971503456789',
                'country': 'South Korea',
                'category': 'Electronics',
                'quality_score': 4.7,
                'delivery_score': 4.6,
                'price_score': 4.3,
                'total_orders': 234,
                'is_active': True,
            },
            {
                'name': 'Smart Device Solutions',
                'contact_person': 'Fatima Zahra',
                'email': 'fatima@smartdevices.com',
                'phone': '+971504567890',
                'country': 'Japan',
                'category': 'Smart Devices',
                'quality_score': 4.8,
                'delivery_score': 4.7,
                'price_score': 4.1,
                'total_orders': 167,
                'is_active': True,
            },
            {
                'name': 'Digital Accessories Co.',
                'contact_person': 'Omar Khalil',
                'email': 'omar@digitalacc.com',
                'phone': '+971505678901',
                'country': 'Thailand',
                'category': 'Accessories',
                'quality_score': 4.1,
                'delivery_score': 3.9,
                'price_score': 4.6,
                'total_orders': 76,
                'is_active': True,
            },
            {
                'name': 'Premium Tech Suppliers',
                'contact_person': 'Layla Ahmed',
                'email': 'layla@premiumtech.com',
                'phone': '+971506789012',
                'country': 'Germany',
                'category': 'Premium Electronics',
                'quality_score': 4.9,
                'delivery_score': 4.8,
                'price_score': 4.0,
                'total_orders': 312,
                'is_active': True,
            },
            {
                'name': 'Budget Electronics Ltd.',
                'contact_person': 'Yusuf Ibrahim',
                'email': 'yusuf@budgetelec.com',
                'phone': '+971507890123',
                'country': 'India',
                'category': 'Budget Electronics',
                'quality_score': 3.8,
                'delivery_score': 3.6,
                'price_score': 4.8,
                'total_orders': 45,
                'is_active': True,
            },
            {
                'name': 'Innovation Tech Group',
                'contact_person': 'Aisha Rahman',
                'email': 'aisha@innovationtech.com',
                'phone': '+971508901234',
                'country': 'USA',
                'category': 'Innovation',
                'quality_score': 4.6,
                'delivery_score': 4.4,
                'price_score': 4.2,
                'total_orders': 198,
                'is_active': True,
            },
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            # Assign a creator to the supplier
            creator = random.choice(users)
            supplier_data['created_by'] = creator
            
            supplier, created = Supplier.objects.get_or_create(
                email=supplier_data['email'],
                defaults=supplier_data
            )
            suppliers.append(supplier)
        
        # Create sourcing requests
        request_types = ['new_supplier', 'replenishment', 'new_product', 'sample']
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['submitted', 'approved', 'in_progress', 'completed', 'cancelled']
        
        # Get users for sellers
        users = User.objects.filter(is_staff=True)
        if not users.exists():
            self.stdout.write(self.style.ERROR('No staff users found. Please create users first.'))
            return
        
        sourcing_requests = []
        for i in range(15):
            request_type = random.choice(request_types)
            priority = random.choice(priorities)
            status = random.choice(statuses)
            seller = random.choice(users)
            supplier = random.choice(suppliers) if status in ['approved', 'in_progress', 'completed'] else None
            
            # Generate request number
            request_number = f"SR-{timezone.now().year}-{str(i+1).zfill(4)}"
            
            # Set product name based on request type
            if request_type == 'new_product':
                product_name = f"New Product {i+1}"
            elif request_type in ['replenishment', 'sample'] and products:
                product = random.choice(products)
                product_name = product.name_en
            else:
                product_name = f"Product {i+1}"
            
            # Create sourcing request
            request = SourcingRequest.objects.create(
                request_number=request_number,
                seller=seller,
                supplier=supplier,
                product_name=product_name,
                carton_quantity=random.randint(10, 100),
                unit_quantity=random.randint(50, 500),
                source_country=random.choice(['China', 'India', 'Thailand', 'South Korea', 'Japan']),
                destination_country='UAE',
                finance_source=random.choice(['self_financed', 'bank_loan', 'investor']),
                supplier_contact=f"Contact {i+1}",
                supplier_phone=f"+971{random.randint(500000000, 599999999)}",
                cost_per_unit=random.uniform(50, 500),
                shipping_cost=random.uniform(100, 1000),
                customs_fees=random.uniform(50, 300),
                weight=random.uniform(0.5, 5.0),
                dimensions=f"{random.randint(20, 50)}x{random.randint(15, 40)}x{random.randint(5, 20)}",
                priority=priority,
                status=status,
                notes=f"This is a {request_type} request for {product_name}. Priority: {priority}",
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
            sourcing_requests.append(request)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(suppliers)} suppliers and {len(sourcing_requests)} sourcing requests.'
            )
        ) 