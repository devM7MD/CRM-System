from django.core.management.base import BaseCommand
from django.core.files import File
from sellers.models import Product
from users.models import User
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Test image upload functionality'

    def handle(self, *args, **options):
        # Create a test image file
        test_image_path = os.path.join(settings.MEDIA_ROOT, 'test_image.txt')
        
        # Create a simple test file
        with open(test_image_path, 'w') as f:
            f.write('This is a test image file')
        
        # Get the first user as seller
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
        
        # Create a test product with image
        try:
            product = Product.objects.create(
                name_en='Test Product with Image',
                name_ar='منتج تجريبي مع صورة',
                code='TEST001',
                description='This is a test product with an image',
                selling_price=99.99,
                purchase_price=50.00,
                seller=user
            )
            
            # Add the test image
            with open(test_image_path, 'rb') as f:
                product.image.save('test_image.txt', File(f), save=True)
            
            self.stdout.write(self.style.SUCCESS(f'Created test product: {product.name_en}'))
            self.stdout.write(f'Image URL: {product.image.url}')
            self.stdout.write(f'Image path: {product.image.path}')
            
            # Clean up test file
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test product: {str(e)}')) 