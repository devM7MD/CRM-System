from django.shortcuts import render, HttpResponse
from django.http import HttpRequest

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
    return render(request, 'pages/auth/login.html', {})

def register(request: HttpRequest):
    return render(request, 'pages/auth/register.html', {})

def forgot_password(request: HttpRequest):
    return render(request, 'pages/auth/resetpassword.html', {})