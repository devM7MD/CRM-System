from django.shortcuts import redirect, render, HttpResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def index(request: HttpRequest):
    return render(request, 'pages/landing/index.html', {})

def about(request: HttpRequest):
    return render(request, 'pages/landing/about.html', {})

def services(request: HttpRequest):
    return render(request, 'pages/landing/services.html', {})

def contact(request: HttpRequest):
    return render(request, 'pages/landing/contact.html', {})

def login(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "You have been logged in successfully.")
            return redirect ('index')
        else:
            messages.success(request, "There was an error logging in")
    else:
        return render(request, 'pages/auth/login.html', {})

def register(request: HttpRequest):
    return render(request, 'pages/auth/register.html', {})

def forgot_password(request: HttpRequest):
    return render(request, 'pages/auth/resetpassword.html', {})

def next(request: HttpRequest):
    return render(request, 'pages/auth/next.html', {})

def overview(request: HttpRequest):
    return render(request, 'pages/user/overview.html', {})