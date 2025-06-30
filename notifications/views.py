from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Notification

@login_required
def notification_list(request):
    """Display a list of all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user)
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })

@login_required
@require_POST
@csrf_protect
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        messages.success(request, _("Notification marked as read."))
        return redirect('notifications:notification_list')

@login_required
@require_POST
@csrf_protect
def mark_all_read(request):
    """Mark all notifications as read for the current user."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        messages.success(request, _("All notifications marked as read."))
        return redirect('notifications:notification_list')
