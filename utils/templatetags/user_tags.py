from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def profile_image_url(user):
    """
    Return the URL for a user's profile image, or a default avatar if none exists.
    
    Usage:
    {% load user_tags %}
    <img src="{% profile_image_url user %}" alt="{{ user.get_full_name }}">
    """
    if user.profile_image and user.profile_image.name:
        return user.profile_image.url
    else:
        # Generate a default avatar URL using UI Avatars service
        name = f"{user.first_name}+{user.last_name}" if user.first_name and user.last_name else user.email.split('@')[0]
        return f"https://ui-avatars.com/api/?name={name}"

@register.simple_tag
def profile_image_tag(user, css_class="h-10 w-10 rounded-full", alt_text=None):
    """
    Return a complete img tag for a user's profile image.
    
    Usage:
    {% load user_tags %}
    {% profile_image_tag user "h-8 w-8 rounded-full" %}
    """
    if not alt_text:
        alt_text = getattr(user, 'get_full_name', lambda: user.email.split('@')[0])()
    
    src = profile_image_url(user)
    return format_html('<img class="{}" src="{}" alt="{}">', css_class, src, alt_text) 