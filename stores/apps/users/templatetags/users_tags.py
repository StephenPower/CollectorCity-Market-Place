import datetime
import logging

from django import template
from django.utils.translation import ugettext as _

from sell.models import Cart

register = template.Library()

@register.filter
def is_admin_shop(user, shop):
    if user.is_authenticated():
        return shop.admin == user
    else:
        return False


@register.filter
def is_bidder(shop, user):
    #return user.is_authenticated() and (user.is_superuser == False and user.is_staff == False)
    return user.is_authenticated() and not is_owner(shop, user)

@register.filter
def is_owner(shop, user):
    return user.is_authenticated and shop.is_admin(user)


@register.filter
def total_cart_items(user, shop):
    cart = Cart.objects.filter(shop=shop, bidder=user).get()
    return cart.total_items()
    
@register.filter
def ago(user):
    time = datetime.datetime.now() - user.last_login
    days = time.days
    s = time.seconds
    hours = s // 3600 
    s = s - (hours * 3600)
    minutes = s // 60
    #seconds = s - (minutes * 60)
    if days > 0:
        if days == 1:
            result = '%s day ' % days
        else:
            result = '%s days ' % days

        if hours == 1:
            result += '%s hour' % hours
        else:
            result += '%s hours' % hours
        #result = '%sd %sh' % (days, hours)
    elif hours > 0:
        if hours == 1:
            result = '%s hour ' % hours
        else:
            result = '%s hours ' % hours

        if minutes == 1:
            result += '%s minute' % minutes
        else:
            result += '%s minutes' % minutes
        #result = '%sh %sm' % (hours, minutes)
    else:
        if minutes == 0:
            return _("Now login")
        elif minutes == 1:
            result = '%s minute' % minutes
        else:
            result = '%s minutes' % minutes
            
    return _("Latest activity %s ago" % result)
    
    return user.is_authenticated() and (user.is_superuser == False and user.is_staff == False)