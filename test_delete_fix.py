#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_fulfillment.settings')
django.setup()

from sellers.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def test_delete_product():
    """Test delete product functionality"""
    print("Testing delete product functionality...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'full_name': 'Test User',
            'phone_number': '+971501234567'
        }
    )
    
    # Create a test product that can be deleted
    import time
    timestamp = int(time.time())
    product = Product.objects.create(
        name_en=f"Test Product {timestamp}",
        name_ar=f"منتج تجريبي {timestamp}",
        code=f"TEST_DELETE_{timestamp}",
        description="A test product for deletion",
        selling_price=99.99,
        purchase_price=50.00,
        stock_quantity=10,
        seller=user
    )
    
    print(f"Created test product: {product.name_en} (ID: {product.id})")
    
    # Test the delete endpoint
    url = f"http://127.0.0.1:8000/inventory/products/{product.id}/delete/"
    
    try:
        response = requests.post(url, data={})
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            
            # Check if product was actually deleted
            try:
                Product.objects.get(id=product.id)
                print("❌ Product still exists in database")
            except Product.DoesNotExist:
                print("✅ Product successfully deleted from database")
        else:
            print(f"❌ Delete request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing delete: {e}")
    
    # Clean up any remaining test products
    test_products = Product.objects.filter(name_en__startswith="Test Product")
    if test_products.exists():
        print(f"Cleaning up {test_products.count()} test products...")
        test_products.delete()

if __name__ == "__main__":
    test_delete_product() 