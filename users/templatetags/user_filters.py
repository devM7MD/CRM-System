from django import template

register = template.Library()

@register.filter
def get_first_name(full_name):
    """Get the first name from a full name"""
    if full_name:
        return full_name.split()[0] if full_name.split() else ''
    return ''

@register.filter
def get_last_name(full_name):
    """Get the last name from a full name"""
    if full_name:
        parts = full_name.split()
        return ' '.join(parts[1:]) if len(parts) > 1 else ''
    return '' 