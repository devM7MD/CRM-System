from django.core.management.base import BaseCommand
from django.core.files import File
from sellers.models import Product
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import io

class Command(BaseCommand):
    help = 'Add real image files to products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        if not products.exists():
            self.stdout.write('No products found.')
            return
        
        self.stdout.write(f'Found {products.count()} products.')
        
        for product in products:
            try:
                # Create a simple image for the product
                img = Image.new('RGB', (300, 300), color='white')
                draw = ImageDraw.Draw(img)
                
                # Add product name to image
                try:
                    # Try to use a default font
                    font = ImageFont.load_default()
                except:
                    font = None
                
                # Draw product name
                text = product.name_en[:20]  # Limit text length
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (300 - text_width) // 2
                y = (300 - text_height) // 2
                
                draw.text((x, y), text, fill='black', font=font)
                
                # Save image to bytes
                img_io = io.BytesIO()
                img.save(img_io, format='PNG')
                img_io.seek(0)
                
                # Save to product
                filename = f'product_{product.id}.png'
                product.image.save(filename, File(img_io), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Added image to {product.name_en}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding image to {product.name_en}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Finished adding real images.')) 