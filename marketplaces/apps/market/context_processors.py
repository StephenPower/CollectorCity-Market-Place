from django.conf import settings


def marketplace(request):
    """
        Add current market to the dns
    """
    return {'marketplace': request.marketplace}

