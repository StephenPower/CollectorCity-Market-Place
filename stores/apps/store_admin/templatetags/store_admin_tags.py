import urllib
import copy
from django import template
from market_buy.models import Show
register = template.Library()

@register.filter
def will_go_show(show, shop):
    return show.will_go_show(shop)

@register.filter
def my_show(show, shop):
    return show.my_show(shop)

@register.filter
def update_filters(params, value):
    k, v = value.split('=')
    new_params = copy.deepcopy(params) 
    new_params.update({k: v})
    return urllib.urlencode(new_params)

@register.filter
def encode_filters(filters):
    return urllib.urlencode(filters)