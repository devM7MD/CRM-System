from django.core.management.base import BaseCommand
from sellers.models import Product
import os

class Command(BaseCommand):
    help = 'Check product images and their URLs'

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        self.stdout.write(f"Total products: {products.count()}")
        
        for product in products:
            self.stdout.write(f"\nProduct: {product.name_en} (ID: {product.id})")
            if product.image:
                self.stdout.write(f"  Image field: {product.image}")
                self.stdout.write(f"  Image URL: {product.image.url}")
                self.stdout.write(f"  Image path: {product.image.path}")
                
                # Check if file exists
                if os.path.exists(product.image.path):
                    self.stdout.write(f"  File exists: Yes")
                    self.stdout.write(f"  File size: {os.path.getsize(product.image.path)} bytes")
                else:
                    self.stdout.write(f"  File exists: No")
            else:
                self.stdout.write(f"  No image") 