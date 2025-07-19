import json
import requests
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .models import BugReport, BugReportImage
from .forms import BugReportForm

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1395477012142886963/IQ994feTGf3iArd8Mbt2FXiEuT6V0b0UQxY0bWUvuHvEix43uWvU3FFUqJwq4xVREDMc"

@login_required
def report_bug(request):
    """View for reporting a bug."""
    if request.method == 'POST':
        form = BugReportForm(request.POST, request.FILES)
        if form.is_valid():
            bug_report = form.save(commit=False)
            bug_report.reporter = request.user
            bug_report.page_url = request.POST.get('page_url', '')
            bug_report.browser_info = request.POST.get('browser_info', '')
            bug_report.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for image in images:
                BugReportImage.objects.create(
                    bug_report=bug_report,
                    image=image
                )
            
            # Send to Discord
            try:
                send_to_discord(bug_report)
                messages.success(request, 'Bug report submitted successfully and sent to the development team!')
            except Exception as e:
                messages.warning(request, f'Bug report saved but failed to send to Discord: {str(e)}')
            
            return redirect('dashboard:index')
    else:
        form = BugReportForm()
    
    return render(request, 'bug_reports/report_bug.html', {'form': form})

@csrf_exempt
@require_http_methods(["POST"])
def ajax_report_bug(request):
    """AJAX endpoint for bug reporting."""
    try:
        # Handle FormData (multipart form data with files)
        form = BugReportForm(request.POST, request.FILES)
        
        if form.is_valid():
            bug_report = form.save(commit=False)
            bug_report.reporter = request.user
            bug_report.page_url = request.POST.get('page_url', '')
            bug_report.browser_info = request.POST.get('browser_info', '')
            bug_report.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for image in images:
                BugReportImage.objects.create(
                    bug_report=bug_report,
                    image=image
                )
            
            # Send to Discord
            try:
                send_to_discord(bug_report)
                return JsonResponse({
                    'success': True,
                    'message': 'Bug report submitted successfully and sent to the development team!'
                })
            except Exception as e:
                return JsonResponse({
                    'success': True,
                    'message': f'Bug report saved but failed to send to Discord: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error submitting bug report: {str(e)}'
        })

def serve_bug_image(request, image_id):
    """Serve bug report images publicly for Discord embeds."""
    try:
        bug_image = BugReportImage.objects.get(id=image_id)
        if bug_image.image:
            # Read the image file
            with open(bug_image.image.path, 'rb') as f:
                image_data = f.read()
            
            # Determine content type
            content_type = 'image/jpeg'  # Default
            if bug_image.image.name.lower().endswith('.png'):
                content_type = 'image/png'
            elif bug_image.image.name.lower().endswith('.gif'):
                content_type = 'image/gif'
            
            response = HttpResponse(image_data, content_type=content_type)
            response['Access-Control-Allow-Origin'] = '*'  # Allow Discord to access
            return response
    except BugReportImage.DoesNotExist:
        pass
    
    return HttpResponse(status=404)

def upload_image_to_imgur(image_path):
    """Upload image to Imgur and return the URL."""
    try:
        # For now, we'll use a simple approach - you can replace this with Imgur API or other image hosting
        # This is a placeholder - in production, you'd want to use a proper image hosting service
        return None
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def send_to_discord(bug_report):
    """Send bug report to Discord webhook."""
    # Create embed
    embed = {
        "title": f"🐛 Bug Report: {bug_report.title}",
        "description": bug_report.description,
        "color": get_priority_color(bug_report.priority),
        "fields": [
            {
                "name": "Reporter",
                "value": bug_report.reporter.get_full_name(),
                "inline": True
            },
            {
                "name": "Priority",
                "value": bug_report.get_priority_display(),
                "inline": True
            },
            {
                "name": "Status",
                "value": bug_report.get_status_display(),
                "inline": True
            },
            {
                "name": "Page URL",
                "value": bug_report.page_url if bug_report.page_url else "Not specified",
                "inline": False
            },
            {
                "name": "Browser Info",
                "value": bug_report.browser_info if bug_report.browser_info else "Not specified",
                "inline": False
            },
            {
                "name": "Reported At",
                "value": bug_report.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True
            }
        ],
        "footer": {
            "text": "Atlas Service - Bug Report System"
        },
        "timestamp": bug_report.created_at.isoformat()
    }
    
    # Add images if any
    if bug_report.images.exists():
        image_urls = []
        for image in bug_report.images.all():
            # Create a direct URL to serve the image
            if hasattr(settings, 'SITE_URL'):
                base_url = settings.SITE_URL
            else:
                base_url = 'http://5.189.156.89'  # Default for development
            
            image_url = f"{base_url}/bug-reports/image/{image.id}/"
            image_urls.append(image_url)
        
        if image_urls:
            # Add image URLs to the embed
            embed["fields"].append({
                "name": "Screenshots",
                "value": f"{len(image_urls)} image(s) attached\n" + "\n".join([f"• [View Image]({url})" for url in image_urls]),
                "inline": False
            })
            
            # Add the first image as the embed thumbnail if available
            if image_urls:
                embed["thumbnail"] = {
                    "url": image_urls[0]
                }
    
    # Prepare Discord message
    discord_data = {
        "username": "Atlas Service",
        "avatar_url": "https://cdn.discordapp.com/avatars/123456789/abcdef.png",  # Replace with actual avatar
        "embeds": [embed]
    }
    
    # Send to Discord
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=discord_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 204:
        # Success - Discord returns 204 for successful webhook
        return True
    else:
        raise Exception(f"Discord webhook failed with status {response.status_code}")

def get_priority_color(priority):
    """Get Discord embed color based on priority."""
    colors = {
        'low': 0x00ff00,      # Green
        'medium': 0xffff00,   # Yellow
        'high': 0xff8000,     # Orange
        'critical': 0xff0000   # Red
    }
    return colors.get(priority, 0x808080)  # Default gray
