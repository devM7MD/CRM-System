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
from django.views.generic.base import RedirectView, TemplateView
# Removed i18n imports as we're using English only
# from utils import views as util_views

# URL patterns - no language prefix needed
urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('sellers/', include('sellers.urls')),
    path('inventory/', include('inventory.urls')),
    path('sourcing/', include('sourcing.urls')),
    path('orders/', include('orders.urls')),
    path('callcenter/', include('callcenter.urls')),
    path('packaging/', include('packaging.urls')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('finance/', include('finance.urls')),
    path('followup/', include('followup.urls')),
    path('subscribers/', include('subscribers.urls', namespace='subscribers')),
    path('roles/', include('roles.urls')),
    path('settings/', include('settings.urls')),
    path('bug-reports/', include('bug_reports.urls')),
    # Landing pages
    path('', include('landing.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Redirect accounts/login to users/login
    path('accounts/login/', RedirectView.as_view(pattern_name='users:login'), name='login_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Serve static files from STATICFILES_DIRS in production
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

