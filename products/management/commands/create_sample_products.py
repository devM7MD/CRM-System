from django.core.management.base import BaseCommand
from products.models import Product
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample products for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample products...')
        
        # Sample products data
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest iPhone with advanced camera system',
                'price': 4499.00,
                'sku': 'IPH15PRO',
                'stock': 50
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Premium Android smartphone with AI features',
                'price': 3999.00,
                'sku': 'SAMS24',
                'stock': 45
            },
            {
                'name': 'MacBook Air M3',
                'description': 'Lightweight laptop with powerful M3 chip',
                'price': 5999.00,
                'sku': 'MBAIRM3',
                'stock': 30
            },
            {
                'name': 'iPad Pro 12.9',
                'description': 'Professional tablet for creative work',
                'price': 3499.00,
                'sku': 'IPADPRO12',
                'stock': 40
            },
            {
                'name': 'AirPods Pro',
                'description': 'Wireless earbuds with noise cancellation',
                'price': 899.00,
                'sku': 'AIRPODSPRO',
                'stock': 100
            },
            {
                'name': 'Apple Watch Series 9',
                'description': 'Smartwatch with health monitoring',
                'price': 1499.00,
                'sku': 'AWATCH9',
                'stock': 60
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Premium noise-cancelling headphones',
                'price': 1299.00,
                'sku': 'SONYWH5',
                'stock': 35
            },
            {
                'name': 'DJI Mini 3 Pro',
                'description': 'Compact drone with 4K camera',
                'price': 2999.00,
                'sku': 'DJIMINI3',
                'stock': 25
            },
            {
                'name': 'GoPro Hero 11',
                'description': 'Action camera for extreme sports',
                'price': 1899.00,
                'sku': 'GOPRO11',
                'stock': 40
            },
            {
                'name': 'Nintendo Switch OLED',
                'description': 'Gaming console with OLED screen',
                'price': 1299.00,
                'sku': 'NSWITCH',
                'stock': 70
            }
        ]
        
        products_created = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock']
                }
            )
            
            if created:
                products_created += 1
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {products_created} new products!')
        ) 