from django.shortcuts import render, HttpResponse
from django.http import HttpRequest

# Create your views here.

def index(request: HttpRequest):
    return render(request, 'index.html', {})

def administrator(request: HttpRequest):
    return render(request, 'administrator.html', {})