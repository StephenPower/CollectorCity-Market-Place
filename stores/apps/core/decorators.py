from django.http import HttpResponseRedirect, Http404
from django.conf import settings


def staff_required(func):
    def decorator(request,*args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())
#        else:
#            if request.shop.admin != request.user:
#                return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())
        return func(request, *args, **kwargs)
    return decorator

def superuser_required(func):
    def decorator(request,*args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())
        return func(request, *args, **kwargs)
    return decorator

def shop_required(func):
    def decorator(request,*args, **kwargs):
        if not hasattr(request, 'shop') or request.shop is None:
            raise Http404
        return func(request, *args, **kwargs)
    return decorator

def shop_admin_required(func):
    """
    Make another a function more beautiful.
    """
    def _decorated(request, *args, **kwargs):
        if request.shop and request.shop.admin == request.user:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/")
    return _decorated

def auctions_feature_required(func):
    def decorator(request,*args, **kwargs):
        if not hasattr(request, 'shop') or request.shop is None:
            raise Http404
        if not request.shop.auctions_feature_enabled():
            raise Http404
        return func(request, *args, **kwargs)
    return decorator

def add_page_feature_enabled(func):
    def decorator(request,*args, **kwargs):
        if not hasattr(request, 'shop') or request.shop is None:
            raise Http404
        if not request.shop.add_pages_feature_enabled():
            raise Http404
        return func(request, *args, **kwargs)
    return decorator