from django.core.management.base import BaseCommand
from django.core.files import File
from sellers.models import Product
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Add sample images to existing products'

    def handle(self, *args, **options):
        products = Product.objects.filter(image='')
        
        if not products.exists():
            self.stdout.write('No products without images found.')
            return
        
        self.stdout.write(f'Found {products.count()} products without images.')
        
        # Create sample image files for each product
        for i, product in enumerate(products):
            # Create a sample image file
            sample_image_path = os.path.join(settings.MEDIA_ROOT, f'sample_image_{product.id}.txt')
            
            # Create a simple test file with product info
            with open(sample_image_path, 'w') as f:
                f.write(f'Sample image for {product.name_en}')
            
            try:
                # Add the sample image to the product
                with open(sample_image_path, 'rb') as f:
                    product.image.save(f'sample_image_{product.id}.txt', File(f), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Added image to {product.name_en}'))
                
                # Clean up the temporary file
                if os.path.exists(sample_image_path):
                    os.remove(sample_image_path)
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding image to {product.name_en}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Finished adding sample images.')) 