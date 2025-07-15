"""
URL configuration for crm_fulfillment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.conf.urls.i18n import i18n_patterns

# Base URL patterns without language prefix
urlpatterns = [
    # Language settings
    path('i18n/', include('django.conf.urls.i18n')),
]

# URL patterns with language prefix
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('sellers/', include('sellers.urls')),
    path('inventory/', include('inventory.urls')),
    path('sourcing/', include('sourcing.urls')),
    path('orders/', include('orders.urls')),
    path('callcenter/', include('callcenter.urls')),
    path('packaging/', include('packaging.urls')),
    path('delivery/', include('delivery.urls')),
    path('finance/', include('finance.urls')),
    path('followup/', include('followup.urls')),
    path('subscribers/', include('subscribers.urls', namespace='subscribers')),
    
    # Landing pages
    path('', include('landing.urls')),
    
    # Redirect accounts/login to users/login
    path('accounts/login/', RedirectView.as_view(pattern_name='users:login'), name='login_redirect'),
    
    # Add prefix_default_language=False to not have a language prefix for the default language
    prefix_default_language=settings.PREFIX_DEFAULT_LANGUAGE
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
