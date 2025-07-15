from django.shortcuts import render, redirect
from django.utils.translation import activate, get_language, gettext_lazy as _
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

def home(request):
    """
    الصفحة الرئيسية للموقع
    """
    context = {
        'title': _('AS Fulfillment & Delivery Services'),
        'subtitle': _('Your trusted partner 🌍 | From sourcing to perfect delivery 📦'),
    }
    return render(request, 'landing/home.html', context)

def about(request):
    """
    صفحة من نحن
    """
    context = {
        'title': _('About Us'),
        'subtitle': _('Why Choose Atlas Fulfillment?'),
    }
    return render(request, 'landing/about.html', context)

def services(request):
    """
    صفحة الخدمات
    """
    services_list = [
        {
            'icon': '🌍',
            'title': _('Import from Global Markets'),
            'description': _('We help you import goods from the largest markets, ensuring safe and efficient handling.')
        },
        {
            'icon': '🏭',
            'title': _('Advanced Storage Services'),
            'description': _('We provide modern warehouses equipped with the latest technologies to store your goods safely and efficiently.')
        },
        {
            'icon': '📞',
            'title': _('Professional Order Confirmation'),
            'description': _('Our specialized team works with high precision to confirm orders, ensuring the best confirmation rate and increasing customer satisfaction.')
        },
        {
            'icon': '🎁',
            'title': _('Perfect Packaging'),
            'description': _('We offer innovative and high-quality packaging services to meet market demands and enhance the value of your products.')
        },
        {
            'icon': '🚚',
            'title': _('Fast and Secure Delivery'),
            'description': _('We guarantee the delivery of goods to end customers on time and with the highest safety standards.')
        },
        {
            'icon': '📸',
            'title': _('Product Photography (Soon)'),
            'description': _('We are working on providing a professional product photography service, so you can display your products attractively and professionally on your sales platforms.')
        }
    ]
    
    context = {
        'title': _('Our Services'),
        'services': services_list
    }
    return render(request, 'landing/services.html', context)

def how_it_works(request):
    """
    صفحة كيفية العمل معنا
    """
    steps = [
        {
            'number': '1️⃣',
            'title': _('Register and Choose a Product'),
            'description': _('After registering on our site in a few simple steps, you can start choosing the products you want to import or store.')
        },
        {
            'number': '2️⃣',
            'title': _('Add Orders via a Dedicated Platform'),
            'description': _('Use our dedicated platform to add orders with ease. The platform is designed to be simple and effective, allowing you to manage your orders with transparency and flexibility.')
        },
        {
            'number': '3️⃣',
            'title': _('Track Order Confirmation and Delivery'),
            'description': _('Let our professional team handle order confirmations with customers and ensure they are delivered quickly and safely.')
        },
        {
            'number': '4️⃣',
            'title': _('Receive Your Money with Full Transparency'),
            'description': _('After the successful delivery of orders, you will receive your dues quickly and transparently. We are keen to provide a hassle-free experience.')
        }
    ]
    
    context = {
        'title': _('How to work with us? It\'s very simple!'),
        'steps': steps
    }
    return render(request, 'landing/how_it_works.html', context)

def faq(request):
    """
    صفحة الأسئلة الشائعة
    """
    faqs = [
        {
            'question': _('Can I start working with Atlas Fulfillment?'),
            'answer': _('You can start easily by registering on our website, after which you can choose the products you want to import or store. Our team will provide full support throughout the process.')
        },
        {
            'question': _('Can I import from any country?'),
            'answer': _('Yes, we help you import products from global markets such as China, Dubai, Europe, and others. We have a specialized team that professionally manages sourcing operations to ensure goods arrive safely and on time.')
        },
        {
            'question': _('Does the company only provide storage services, or are there other services?'),
            'answer': _('We offer integrated logistics solutions including: secure storage, professional packaging, order confirmation service, fast delivery, and more. We are also working on providing a product photography service soon.')
        },
        {
            'question': _('How long does it take to deliver orders to customers?'),
            'answer': _('We always strive to deliver orders on time based on the geographical location and the nature of the product. Our team coordinates all steps to ensure fast and secure delivery.')
        },
        {
            'question': _('How can I track the status of my orders?'),
            'answer': _('We provide a dedicated platform for order management, where you can track the status of each order with transparency and flexibility. You will also receive regular updates on the order status until it is delivered to the final customers.')
        },
        {
            'question': _('How are my profits transferred to me?'),
            'answer': _('After the successful delivery of orders, your dues are transferred quickly and transparently. We adhere to the highest standards of security and clarity in financial dealings.')
        },
        {
            'question': _('Can I trust your storage services?'),
            'answer': _('Of course! We provide modern warehouses equipped with the latest technologies to ensure your goods are stored safely and efficiently. We adhere to the highest standards of quality and security to protect your products.')
        },
        {
            'question': _('What happens if there is damage to the products during delivery?'),
            'answer': _('We take full responsibility for the safety of products during storage and delivery. In the event of any unexpected damage, we will compensate you according to the company\'s policy.')
        },
        {
            'question': _('What if a part of the goods remains in the warehouse and is not sold in the same country? Can I move it to another country?'),
            'answer': _('Yes, if you have goods left in the warehouse that were not sold in the same country, you can easily move them to another country or even to Africa. We provide flexible solutions for redistributing your goods according to market needs and your business plans.')
        }
    ]
    
    context = {
        'title': _('Frequently Asked Questions'),
        'faqs': faqs
    }
    return render(request, 'landing/faq.html', context)

def contact(request):
    """
    Contact page with form handling
    """
    context = {
        'title': _('Contact Us'),
        'email': 'info@asfulfillment.com',
        'phone': '+971 50 123 4567',
        'address': _('Dubai, United Arab Emirates'),
        'social_links': {
            'facebook': 'https://facebook.com/asfulfillment',
            'instagram': 'https://instagram.com/asfulfillment',
            'twitter': 'https://twitter.com/asfulfillment',
            'linkedin': 'https://linkedin.com/company/asfulfillment',
        }
    }
    
    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically save the contact form data to the database
        # or send an email to the administrator
        
        # For now, just show a success message
        messages.success(request, _('Thank you for contacting us! We will get back to you soon.'))
        
        # Redirect to avoid form resubmission on refresh
        if request.path == reverse('landing:contact'):
            return redirect('landing:contact')
        else:
            return redirect('landing:home')
    
    return render(request, 'landing/contact.html', context)

def privacy(request):
    """
    صفحة سياسة الخصوصية
    """
    context = {
        'title': _('Privacy Policy'),
    }
    return render(request, 'landing/privacy.html', context)

def terms(request):
    """
    صفحة شروط الخدمة
    """
    context = {
        'title': _('Terms of Service'),
    }
    return render(request, 'landing/terms.html', context) 

def switch_language(request, language_code):
    """
    Custom language switcher for landing pages only.
    This doesn't affect the dashboard language settings.
    """
    next_url = request.GET.get('next', '/')
    
    # Get the current URL name and arguments
    try:
        resolver = resolve(next_url)
        view_name = resolver.view_name
        args = resolver.args
        kwargs = resolver.kwargs
        
        # Only process language switch for landing pages
        if view_name.startswith('landing:'):
            # Activate the requested language
            activate(language_code)
            
            # Set the language cookie for landing pages only
            response = HttpResponseRedirect(next_url)
            response.set_cookie(
                'landing_language', 
                language_code,
                max_age=60*60*24*365,  # 1 year
                path='/',  # Only set for landing pages
                samesite='Lax'
            )
            return response
    except:
        pass
    
    # Default fallback
    return HttpResponseRedirect(next_url) 