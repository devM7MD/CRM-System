from django.shortcuts import redirect
from django.conf import settings

def switch_language(request, language_code):
    """
    Switches the language and redirects to the homepage for that language.
    """
    # Fallback to the default language if the selected language is not supported
    if language_code not in [lang[0] for lang in settings.LANGUAGES]:
        language_code = settings.LANGUAGE_CODE

    # Determine the redirect URL based on the language
    # For the default language, we might not want a prefix (e.g., /en/)
    if language_code == settings.LANGUAGE_CODE and not getattr(settings, 'PREFIX_DEFAULT_LANGUAGE', True):
        redirect_url = '/'
    else:
        redirect_url = f'/{language_code}/'

    # Create a response to redirect to the new URL
    response = redirect(redirect_url)

    # Set the language cookie to remember the user's choice
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language_code,
        max_age=getattr(settings, 'LANGUAGE_COOKIE_AGE', None),
        path=getattr(settings, 'LANGUAGE_COOKIE_PATH', '/'),
        domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
        secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
        httponly=getattr(settings, 'LANGUAGE_COOKIE_HTTPONLY', False),
        samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', None)
    )

    return response 