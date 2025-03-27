from django.conf import settings

def languages_processor(request):
    """
    Add the list of available languages to the template context
    """
    return {
        'languages': settings.LANGUAGES,
    } 