#import datetime
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _

from bidding.views import my_render
from core.decorators import shop_required
from lots.models import Lot, BidHistory
from preferences.forms import ShippingItemForm
from sell.models import Payment, Sell, CartItem, ShippingData

from sell.templatetags.sell_tags import money_format

@shop_required
@login_required
def my_orders(request):
    my_orders = Sell.objects.filter(shop=request.shop, bidder=request.user)

    inner_q = BidHistory.objects.filter(bidder=request.user, lot__state='A').values_list('lot').distinct().query
    lots_in_auctions = Lot.objects.filter(pk__in=inner_q)
    
    bids_list = []
    for lot in lots_in_auctions:
        history = []    
        for bid in lot.history():
            history.append({'bidder_username': bid.bidder.username,
                            'bid_amount': money_format(bid.bid_amount, request.shop),
                            'bid_time': date(bid.bid_time, 'r'),
                            })      
        image = lot.image()   
        bids_list.append({'url': reverse('bidding_view_lot', args=[lot.id]),
                          #'image': lot.image().image.url_100x100 if lot.image() else None,
                          'title': lot.title,
                          'is_active': lot.is_active(),
                          'count_bids': lot.count_bids(),
                          'current_bid': lot.current_bid(),
                          'time_left': lot.time_left(),
                          'history': history,
                          'image': {
                                    'original': image.image.url if image else None,
                                    'small': image.image.url_100x100 if image else None,
                                    'medium': image.image.url_400x400 if image else None,
                                   }
                          })

    my_orders_list = []
    for sell in my_orders:
        items = []
        for item in sell.sellitem_set.all():
            image = item.product.image()
            items.append({
                          #'image': item.product.image().image.url_100x100 if item.product.image() else None,
                          'url': item.product.get_bidding_url(),
                          'title': item.product.title,
                          'price': money_format(item.price, request.shop),
                          'image': {
                                    'original': image.image.url if image else None,
                                    'small': image.image.url_100x100 if image else None,
                                    'medium': image.image.url_400x400 if image else None,
                                   }
                          })
        payment_history = []    
        for payment in sell.payment.paymenthistory_set.all():
            payment_history.append({
                                    'date_time': date(payment.date_time, 'r'),
                                    'state': payment.get_state_display(),
                                    })

        shipping_history = []    
        for shipping in sell.shipping.shippinghistory_set.all():
            shipping_history.append({
                                    'date_time': date(shipping.date_time, 'r'),
                                    'state': shipping.get_state_display(),
                                    })
            
        my_orders_list.append({'id': sell.id,
                               'date_time': date(sell.date_time, 'r'),
                               'total': money_format(sell.total, request.shop),
                               'payment_history': payment_history,
                               'shipping_history': shipping_history,
                               'item_set': items,
                              })
        
    param = {
             'bids': bids_list,
             'my_orders': my_orders_list,
             'page_title': 'My Orders',
             'page_description': 'My Orders',
             }
    
    return HttpResponse(my_render(request, param, 'my_orders'))        


@shop_required
def my_shopping(request):
    my_cart = request.cart
    
    my_orders = Sell.objects.filter(shop=request.shop, bidder=request.user)
     
    cart_list = []
    for item in my_cart.cartitem_set.all():
        if item.product.type() == "Item":
            #url = reverse('bidding_view_item', args=[item.product.id])
            url_remove = reverse('remove_from_cart', args=[item.id])
        else: 
            #url = reverse('bidding_view_lot', args=[item.product.id])
            url_remove = ''
        image = item.product.image()
        cart_list.append({'url': item.product.get_bidding_url(),
                          'title': item.product.title,
                          #'image': item.product.image().image.url_100x100 if item.product.image() else None,
                          'price': money_format(item.price, request.shop),
                          'qty': item.qty,
                          'sub_total': money_format(item.sub_total(), request.shop),
                          'can_remove': (item.product.type() == "Item"),
                          'url_remove': url_remove, 
                          'image': {'original': image.image.url if image else None,
                                    'small': image.image.url_100x100 if image else None,
                                    'medium': image.image.url_400x400 if image else None,
                                   } 
                         })

    param = {
             'cart_items': cart_list,
             'total_cart': money_format(my_cart.total(), request.shop),
             'total': money_format(my_cart.total(), request.shop),
             'page_title': 'My Shopping',
             'page_description': 'My Shopping',
             'url_checkout': reverse('myshopping_checkout_shipping'),
             'clean_cart_url': reverse('clean_cart'),
             }
    
    return HttpResponse(my_render(request, param, 'my_shopping'))


@shop_required
def checkout_shipping(request):
    from sell.forms import ShippingDataForm
    
    if request.method == 'POST':
        shipping_form = ShippingDataForm(data=request.POST)
        if shipping_form.is_valid():
            #profile = request.user.get_profile()
            cart = request.cart
            
            try:
                oldshipping = cart.shippingdata
                cart.shippingdata = None
                cart.save()
                oldshipping.delete()
            except:
                pass
            
            shipping = shipping_form.save(commit=False)
            shipping.save()
            
            cart.shippingdata = shipping
            cart.save()
            
            return HttpResponseRedirect(reverse("myshopping_checkout_confirm"))
    else:
        #initial = {'street_address': '13444 Main Street', 'city': 'Springfield', 'state' : 'Maryland', 'zip': '20104', 'country' : 'USA' }
        shipping_form = ShippingDataForm()
        
    return HttpResponse(my_render(request, {'form_shipping': shipping_form.as_p(),
                                            'page_title': 'Shipping',
                                            'page_description': 'Shipping',
                                            'url_home' : reverse("home"),
                                            }, 'shipping'))


def checkout_manual_payment(request):
    from payments.models import ManualPaymentShopSettings
    
    
    id = request.POST.get("manual_payment_id", None)
    payment = get_object_or_404(ManualPaymentShopSettings, pk=id)
    
    if request.method == "POST":
        cart = request.cart
        sell = cart.close(payment_method="%s - %s" % ('Manual Payment', payment.name))
    
    return HttpResponse(my_render(request, {'instructions': payment.instructions,
                                         'page_title': 'Manual payment',
                                         'page_description': 'Manual payment' 
                                         }, 'manual_payment'))


@shop_required
def checkout_confirm(request):
    from payments.gateways.googlecheckout import GoogleCheckoutGateway
    from payments.gateways.paypal import PayPalGateway
    from payments.gateways.braintreegw import BraintreeGateway
    from payments.models import GoogleCheckoutShopSettings, PayPalShopSettings, ManualPaymentShopSettings, BraintreeShopSettings
    #A list of payment method, each payment method know how to render as a link
    #payment_methods = request.shop.get_payment_methods()
    payment_buttons = []
    #profile = request.user.get_profile()
    cart = request.cart
    shop = request.shop
    
    try:   
        google_settings = GoogleCheckoutShopSettings.objects.filter(shop = shop).get()
        googlecheckout_gw = GoogleCheckoutGateway(google_settings.merchant_id, 
                                                  google_settings.merchant_key, 
                                                  debug=True)
        button = googlecheckout_gw.render_button(cart)
        payment_buttons.append(button)
    except GoogleCheckoutShopSettings.DoesNotExist:
        pass

    try:   
        braintree_settings = BraintreeShopSettings.objects.filter(shop = shop).get()
        braintree_gw = BraintreeGateway(braintree_settings.merchant_id, 
                                        braintree_settings.public_key,
                                        braintree_settings.private_key,
                                        )
        button = braintree_gw.render_button(cart)
        payment_buttons.append(button)
    except BraintreeShopSettings.DoesNotExist:
        pass
    
    try:
        paypal_settings = PayPalShopSettings.objects.filter(shop = shop).get()
        paypal_gw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                             password=settings.PAYPAL_PASSWORD,
                             sign=settings.PAYPAL_SIGNATURE,
                             debug=settings.PAYPAL_DEBUG)
        button = paypal_gw.render_button()
        payment_buttons.append(button)
        
        
    except PayPalShopSettings.DoesNotExist:
        pass
    
    
    try:
        manual_payment_settings = ManualPaymentShopSettings.objects.filter(shop = shop)
        url = reverse("myshopping_checkout_manual_payment")
        
        if manual_payment_settings.count():
            button = """
            <div>
                <h3>Manual Payments</h3>\n
                <form name='manual_payment' action='%s' method='POST'>\n
            """ % url
            for idx, payment in enumerate(manual_payment_settings):
                input = '\t<input type="radio" name="manual_payment_id" checked="%d" value="%s"> %s </input><br/>\n' % (1 if idx == 0 else 0, payment.id, payment.name)
                button += input
            button += "<br/>"
            button += "<button class='primaryAction small awesome' type='submit'>Submit</button>\n"
            button += "</form>\n"
            button += "</div>"
            
            logging.debug(button)
            payment_buttons.append(button)
    except Exception, e:
        logging.error(e)
    
#    t = loader.get_template('my_shopping/blocks/confirm.html')
#    c = RequestContext(request, {'cart' : cart,
#                                 'payment_buttons': payment_buttons,})
#    block_confirm = (t.render(c))
    items = []
    for item in cart.cartitem_set.all():
        image = item.product.image()
        items.append({
                      #'image': item.product.image().image.url_100x100 if item.product.image() else None,
                      'title': item.product.title,
                      'price': money_format(item.price, shop),
                      'qty': item.qty,
                      'sub_total': money_format(item.sub_total(), shop),
                      'image': {'original': image.image.url if image else None,
                                'small': image.image.url_100x100 if image else None,
                                'medium': image.image.url_400x400 if image else None,
                               } 
                      })
    
    shippingdata =({'street_address': cart.shippingdata.street_address.title(),
                     'city': cart.shippingdata.city.title(),
                     'state': cart.shippingdata.state.upper(),
                     'zip': cart.shippingdata.zip,
                     'country': cart.shippingdata.country.upper(),
                     })
    
    cart_dic = {'cart_items': items,
                'shippingdata': shippingdata,
                'total': money_format(cart.total(), shop),
                'taxes': money_format(cart.taxes(), shop),
                'shipping_charge': money_format(cart.shipping_charge(), shop),
                'total_with_taxes': money_format(cart.total_with_taxes(), shop),
                }
    
    return HttpResponse(my_render(request, {'cart': cart_dic,
                                            'payment_buttons': payment_buttons,
                                            'page_title': 'Confirm',
                                            'page_description': 'Confirm',
                                            'admin_email': shop.admin.email,                                          
                                           },
                                  'confirm'))


@shop_required    
def remove_from_cart(request, id):
    
    cartitem = get_object_or_404(CartItem, pk=id)
            
    cart = request.cart
    #cart.remove(cartitem)
    cart.remove_one(cartitem)
    
    request.flash['message'] = unicode(_("Product removed from your cart"))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('my_shopping'))

@shop_required    
def clean_cart(request):
    
    cart = request.cart
    cart.clean()
    
    request.flash['message'] = unicode(_("Your cart is empty now!"))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('my_shopping'))
