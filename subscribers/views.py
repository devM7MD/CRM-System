from django.shortcuts import render
from django.http import HttpResponse

def subscribers_list(request):
    # Placeholder: Replace with actual queryset
    return render(request, 'subscribers/subscribers.html', {'subscribers': []})

def add_user(request):
    # Placeholder view for Add User
    return HttpResponse('Add User page coming soon.') 