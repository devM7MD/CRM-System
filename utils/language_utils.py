from django.conf import settings
from django.utils import translation

def get_language_switch_url(request, language_code=None):
    """
    Returns the URL to switch to the specified language.
    If language_code is not provided, it will switch to the other available language.
    """
    current_language = translation.get_language()
    
    if language_code is None:
        # If no language code is provided, switch to the other language
        available_languages = [code for code, name in settings.LANGUAGES]
        if len(available_languages) <= 1:
            return request.get_full_path()
        
        current_index = available_languages.index(current_language) if current_language in available_languages else 0
        next_index = (current_index + 1) % len(available_languages)
        language_code = available_languages[next_index]
    
    # Get the path without language prefix
    path = request.get_full_path()
    
    # If the path starts with a language code, remove it
    for lang_code, lang_name in settings.LANGUAGES:
        if path.startswith(f'/{lang_code}/'):
            path = path[len(lang_code) + 1:]
            break
    
    # Ensure path starts with a slash
    if not path.startswith('/'):
        path = '/' + path
    
    # Add the language code to the path
    if language_code != settings.LANGUAGE_CODE or settings.PREFIX_DEFAULT_LANGUAGE:
        return f'/{language_code}{path}'
    
    return path
