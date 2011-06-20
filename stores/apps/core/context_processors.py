from django.conf import settings


def shop(request):
    """
        Add shop to context
    """
    
    return {'shop': getattr(request, 'shop', None)}


def google_key(request):
    """
        Add the google service key to the Context
    """
    params = {
        'GOOGLE_KEY': getattr(settings, 'GOOGLE_KEY', None),
    }
    
    return params


def default_dns(request):
    """
        Add DNS default, to create shops with default dns
    """
    params = {
        'DEFAULT_DNS': getattr(settings, 'DEFAULT_DNS', None),
    }
    
    return params

def secure_media(request):
    """
        Change MEDIA_URL
    """
    
    if request.is_secure() and hasattr(settings, 'SECURE_MEDIA_URL'):
        return {
            'MEDIA_URL': settings.SECURE_MEDIA_URL,
            'REQUEST_IS_SECURE': True,
        }
    
    return {'REQUEST_IS_SECURE': False}

