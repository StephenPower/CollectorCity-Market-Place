import decimal, logging
import re

from django import template
from sell.models import Payment, Cart
register = template.Library()

@register.filter
def total_pending(shop, user):
    cart = Cart.objects.filter(shop=shop).filter(bidder=user).get()
    total_cart = cart.total()
    try:
        payment = Payment.objects.filter(sell__bidder=user, state_actual__state='PE')[0]
        total_sell = payment.sell.total()
    except Payment.DoesNotExist:
        total_sell = 0
    except Exception, e:
        total_sell = 0
    return total_cart + total_sell
    

@register.filter
def count_pending(shop, user):
    cart = Cart.objects.filter(shop=shop).filter(bidder=user).get()
    total_cart = cart.cartitem_set.all().count()
    try:
        payment = Payment.objects.filter(sell__bidder=user, state_actual__state='PE').get()
        total_sell = payment.sell.sellitem_set.all().count()
    except Payment.DoesNotExist:
        total_sell = 0
    return total_cart + total_sell


@register.filter
def money_format(value, shop):
    context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
    decimal.setcontext(context)
    
    currency_symbol =  shop.preference().checkout_currency
    if currency_symbol is None:
        currency_symbol = '$$'
    
    if currency_symbol == 'USD':
        currency_symbol = '$'
    
    try:
        value = decimal.Decimal(value)
    except Exception,e:
        logging.critical("could not convert value %s to decimal" % value)
        return "%s %s" % (currency_symbol, value)
        
    try:
        amount =  value.quantize(decimal.Decimal('.01'))
    except Exception,e:
        logging.error("could not format value %s as decimal. %s" % (value, e))
        amount = value
    
    amount = "%s %.2f" % (currency_symbol, amount)
    return re.sub("(\.00)$", '', amount)


@register.filter
def money_format2(value, shop):
    context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
    decimal.setcontext(context)
    
    currency_symbol =  shop.preference().checkout_currency
    if currency_symbol is None:
        currency_symbol = '$$'
    
    if currency_symbol == 'USD':
        currency_symbol = '$'
    
    try:
        value = decimal.Decimal(value)
    except Exception,e:
        logging.critical("could not convert value %s to decimal" % value)
        return "%s %s" % (currency_symbol, value)
        
    try:
        amount =  value.quantize(decimal.Decimal('.01'))
    except Exception,e:
        logging.error("could not format value %s as decimal. %s" % (value, e))
        amount = value
    
    amount = "%s %.2f" % (currency_symbol, amount)
    m = re.match(r"(?P<price>[\d\$\W]+)(\.)(?P<fl>[\d]+)$", amount)
    return (m.group('price'), m.group('fl'))

        
@register.filter
def format_price(value, currency_symbol):
    context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
    decimal.setcontext(context)
    
    if currency_symbol is None:
        currency_symbol = '$$'
    
    if currency_symbol == 'USD':
        currency_symbol = '$'
    
    try:
        value = decimal.Decimal(str(value))
    except Exception,e:
        logging.critical("could not convert value %s to decimal" % value)
        return value
    
    value = "%s %.2f" % (currency_symbol, value)
    return re.sub("(\.00)$", '', value)
