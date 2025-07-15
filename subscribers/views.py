from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import Subscriber
from django.http import JsonResponse
from django.db import transaction

User = get_user_model()

@login_required
def subscribers_list(request):
    # First try to get subscribers from the Subscriber model
    subscribers = Subscriber.objects.all()
    
    # If no subscribers found, get all users with 'seller' role
    if not subscribers.exists():
        # Get users with seller role
        seller_users = User.objects.filter(role='seller')
        
        # Convert User objects to a format compatible with the subscribers template
        subscribers_data = []
        for user in seller_users:
            # Create a dictionary that mimics Subscriber model fields
            subscriber_dict = {
                'id': user.id,  # Use 'id' instead of 'pk' to match Subscriber model's primary key field
                'full_name': user.full_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'business_name': user.company_name or '',
                'residence_country': user.country or '',
                'registration_date': user.date_joined,
                'user': user
            }
            # Append to our list
            subscribers_data.append(subscriber_dict)
        
        # Pass the list to the template
        return render(request, 'subscribers/subscribers.html', {'subscribers': subscribers_data, 'from_users': True})
    
    # If there are subscribers in the Subscriber model, just return those
    return render(request, 'subscribers/subscribers.html', {'subscribers': subscribers})

@login_required
def subscriber_detail(request, pk):
    # Try to get a subscriber object first
    try:
        subscriber = Subscriber.objects.get(pk=pk)
    except Subscriber.DoesNotExist:
        # If no subscriber found, try to get a user with 'seller' role
        user = get_object_or_404(User, id=pk, role='seller')
        
        # Create a dictionary that mimics Subscriber model fields
        subscriber = {
            'id': user.id,  # Use 'id' instead of 'pk'
            'full_name': user.full_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'business_name': user.company_name or '',
            'residence_country': user.country or '',
            'registration_date': user.date_joined,
            'user': user,
            'store_link': '',
            'services': []
        }
        return render(request, 'subscribers/subscriber_detail.html', {'subscriber': subscriber, 'from_users': True})
        
    return render(request, 'subscribers/subscriber_detail.html', {'subscriber': subscriber})

@login_required
def add_user(request):
    if request.method == 'POST':
        try:
            # Create User account
            user = User.objects.create(
                email=request.POST['email'],
                full_name=request.POST['full_name'],
                phone_number=request.POST['phone_number'],
                company_name=request.POST['business_name'],
                country=request.POST['residence_country'],
                password=make_password(request.POST['password']),
                is_active=True,
                role='seller'  # Set role as seller
            )
            
            # Create Subscriber profile
            subscriber = Subscriber.objects.create(
                user=user,
                full_name=request.POST['full_name'],
                email=request.POST['email'],
                phone_number=request.POST['phone_number'],
                business_name=request.POST['business_name'],
                residence_country=request.POST['residence_country'],
                store_link=request.POST.get('store_link', ''),
                services=request.POST.getlist('services[]')
            )
            messages.success(request, 'Subscriber added successfully!')
            return redirect('subscribers:detail', pk=subscriber.pk)
        except Exception as e:
            messages.error(request, f'Error creating subscriber: {str(e)}')
            return redirect('subscribers:add_user')
            
    return render(request, 'subscribers/add_user.html')

@login_required
def delete_subscriber(request, pk):
    if request.method == 'POST':
        try:
            # Try to get a subscriber
            try:
                subscriber = Subscriber.objects.get(pk=pk)
                
                # Store the email for logging
                email = subscriber.email
                
                # If there's a linked user account, delete it first (will cascade delete the subscriber)
                if subscriber.user:
                    # If the user deleting is the same as the subscriber's user, don't allow it
                    if subscriber.user == request.user:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'You cannot delete your own account.'
                        })
                        
                    # Delete the User (which will cascade delete the subscriber)
                    subscriber.user.delete()
                else:
                    # If no user is linked, delete the subscriber directly
                    subscriber.delete()
            except Subscriber.DoesNotExist:
                # If no subscriber found, try to delete a user with 'seller' role
                user = get_object_or_404(User, id=pk, role='seller')
                
                # If the user deleting is the same as the user being deleted, don't allow it
                if user == request.user:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You cannot delete your own account.'
                    })
                
                # Store the email for logging
                email = user.email
                
                # Delete the user
                user.delete()
                    
            return JsonResponse({'status': 'success', 'message': f'Subscriber {email} has been permanently deleted.'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error deleting subscriber: {str(e)}'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 