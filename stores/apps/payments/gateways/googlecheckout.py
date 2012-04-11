# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404

from gchecky import model as gmodel
from gchecky.controller import Controller

from core.decorators import shop_required
from sell.models import Cart
from shops.models import Shop
from payments.models import GoogleCheckoutOrder

SANDBOX =  getattr(settings, "GOOGLE_CHECKOUT_SANDBOX", False) 

class GoogleCheckoutGateway(object):
    
    name = "google_checkout"
    
    def __init__(self, merchant_id, merchant_key, debug = True):
        #TODO: Read this from settings
        self.merchant_id = merchant_id.encode('ascii')
        self.merchant_key = merchant_key.encode('ascii')
        self.api_version = 'v2'
        self.work_on_sandbox = SANDBOX     # True for testing, False for production
        self.checkout_currency = 'USD'  # Checkouts only supports (USD , GBP)
        self._controller = None
    
    def controller(self):
        if self._controller is None: 
            controller = Controller(vendor_id=self.merchant_id,
                                    merchant_key=self.merchant_key,
                                    is_sandbox=self.work_on_sandbox,
                                    currency=self.checkout_currency)
            self._controller = controller
        return self._controller
    
        
    def createCart(self, cart):
        """
        Create a shopping cart compatible with gchecky from our local cart.
        @return : a gmodel.checkout_shopping_cart_t
        """
        items = []
        for cartitem in cart.cartitem_set.all():
            item = gmodel.item_t(name=cartitem.product.title,
                                 description=cartitem.product.description,
                                 unit_price=gmodel.price_t(
                                                             value=cartitem.price,
                                                             currency = self.checkout_currency
                                                             ),
                                 quantity=cartitem.qty
                                 )
            items.append(item)
        
        
        
        url_success = "http://%s/payments/success" % (cart.shop.default_dns)
        
        merchant_private_data = "cart_id:%s#shop_id:%s" % (cart.id, cart.shop.id)
        
        shopping_cart = gmodel.shopping_cart_t(items=items, merchant_private_data=merchant_private_data)
        
        support = gmodel.checkout_flow_support_t(
                            edit_cart_url = None,
                            continue_shopping_url = url_success,
                            tax_tables = gmodel.tax_tables_t(
                                merchant_calculated = False,
                                default = gmodel.default_tax_table_t(
                                    tax_rules = [
                                        gmodel.default_tax_rule_t(
                                            shipping_taxed = False,
                                            rate = cart.rate_taxes(),
                                            tax_area = gmodel.tax_area_t(world_area = True)
                                        )
                                    ]
                                )
                            ),
                            shipping_methods = gmodel.shipping_methods_t(
                                flat_rate_shippings = [
                                    gmodel.flat_rate_shipping_t(
                                        name = 'Standard Shipping',
                                        price = gmodel.price_t(
                                                currency = self.checkout_currency,
                                                value = float(str(cart.shipping_charge())),
                                        ),
#                                        allowed_areas = gmodel.allowed_areas_t(
#                                            postal_areas = [gmodel.postal_area_t(
#                                                country_code = 'US',
#                                                )],
#                                        ),
#                                        excluded_areas = gmodel.excluded_areas_t(
#                                            postal_areas = [gmodel.postal_area_t(
#                                                country_code = 'US',
#                                                )],
#                                        ),
                                    )]
                            )
                        )  
        cart = gmodel.checkout_shopping_cart_t(shopping_cart = shopping_cart, checkout_flow_support = support)
        logging.debug(cart)
        return cart

    def processOrder(self, cart):
        """
        @return: An instance of html_order and has the follow fields:
        - cart - signed and base64 encoded XML representing the shopping cart
        - signature - base64 encoded signature (composed from your ID and KEY)
        - url - address where the cart should be sent
        - button - url of the Google Checkout button image
        - xml - the full XML represnting the cart
        - html - the complete html snippet for the GButton - a form with
                 the correct URL, hidden data - GButton is the only visible
                 input.
        """
        processed_cart = self.createCart(cart)
        return self.controller().prepare_order(order=processed_cart)
    
    
    def render_button(self, cart):
        form = self.processOrder(cart).html()
        html = """
        <h3>Google Checkout</h3>
        %s
        """ % form
        return html
    
    
    def process_message(self, data):
        
        notification_type = data["_type"]
        if notification_type == "new-order-notification":
            self.process_new_order_notification(data)
        
        elif notification_type == "authorization-amount-notification":
            self.process_authorization_amount_notification(data)
        
        elif notification_type == "order-state-change-notification":
            self.process_order_state_change_notification(data)
        
        elif notification_type == "risk-information-notification":
            self.process_risk_notification(data)
        
        elif notification_type == "charge-amount-notification":
            self.process_charge_fee_notification(data)
    
        elif notification_type == "refund-amount-notification":
            self.process_refund_notification(data)
            
        else:
            logging.info("Unknown notification message. POST: %s" % data)
        
    def process_charge_fee_notification(self, data):
        order_number = data['google-order-number']
        fee = data['latest-charge-fee.total']        
        logging.info("Charge fee Notification (USD %s) arrived (ignored) for Order <%s>" % (fee, order_number))
        
    def process_refund_notification(self, data):
        order_number = data['google-order-number']
        refund = data["total-refund-amount"]
        logging.info("Refund Notification (USD %s) arrived (ignored) for Order <%s>" % (refund, order_number))
        
    def process_authorization_amount_notification(self, data):
        """
        An <authorization-amount-notification> contains information on the credit card authorized amount and the 
        result of the AVS and CVV checks. The <authorization-amount-notification> is sent after Google Checkout 
        attempts to authorize a buyer's credit card for a new order.
        """
        order_number = data['google-order-number']
        logging.debug("Authorization Amount Notification arrived (ignored)... Order <%s>" % order_number)    
        
        
    def process_risk_notification(self, data):
        """
        link : http://code.google.com/intl/es-AR/apis/checkout/developer/Google_Checkout_XML_API_Notification_API.html#risk_information_notification
        
        Google Checkout sends a risk information notification after completing its risk analysis on a new order. 
        A risk-information-notification includes financial information such as the customer's billing address, 
        a partial credit card number and other values that help you verify that an order is not fraudulent.
        Note: Before shipping the items in the order, you should wait until you have also received the new order
        notification for the order and the authorization
        """
        order_number = data['google-order-number']
        logging.debug("Risk Notification arrived (ignored)... Order <%s>" % order_number)
        
        
    def process_order_state_change_notification(self, data):
        """
        link : http://code.google.com/intl/es-AR/apis/checkout/developer/Google_Checkout_XML_API_Notification_API.html#order_state_change_notification
        
        Google sends an order state change notification to notify you that an order's financial status or
        its fulfillment status has changed. The notification identifies the new financial and fulfillment
        statuses for the order as well as the previous statuses for that order.
        These status changes can be triggered by Order Processing API commands that you send to Google Checkout.
        For example, if you send Google Checkout a <cancel-order> request, Google will respond both 
        synchronously and through the Notification API to inform you that Google Checkout changed the 
        order's status to CANCELLED.
        Note: Before you ship the items in an order, you should ensure that you have already received 
        the new order notification for the order, the risk information notification for the order and an 
        authorization amount notification identifying the chargeable amount.
        """
        order_number = data['google-order-number']
        logging.debug("Order State Change Notification arrived...Order <%s>" % order_number)
        try:
            order = GoogleCheckoutOrder.objects.filter(order_number=order_number).get()
            order.financial_state = data["new-financial-order-state"]
            order.save()
            
            if order.financial_state == "CHARGED":
                order.sell_charged()
                logging.debug("Order confirmed, sell set as paid!")
            elif order.financial_state == "CANCELLED":
                order.sell_cancelled()
                logging.debug("Order was cancelled!")
            else:
                logging.debug("Order not charged yet, sell will not be set as paid...")
                
        except Exception, e:
            raise e
        
    def process_new_order_notification(self, data):
        """
        Before shipping the items in an order, you should wait until you have also received the risk information
        notification for that order as well as the order state change notification informing you that the order's 
        financial state has been updated to CHARGEABLE.
        
        Process a new order notification 
        
        data = {
            ...
            u'buyer-id': [u'851317705418569']
            u'serial-number': [u'500070226120390-00001-7']
            u'google-order-number': [u'500070226120390']
            ...
        }
        """
        buyer_id = data['buyer-id']
        order_number = data['google-order-number']
        type = data["_type"]
        buyer = data["buyer-billing-address.structured-name.first-name"]                       
        order_total = data["order-summary.order-total"]
        
        logging.debug("New google order Notification arrived... Order <%s>" % order_number)
        
        already_processed = True
        try:
            order = GoogleCheckoutOrder.objects.filter(order_number=order_number).get()
        except GoogleCheckoutOrder.DoesNotExist:
            already_processed = False
        
        if already_processed: 
            logging.debug("Notification already processed...")
            return        
               
        try:
            cart_id = parse_merchant_private_data(data)['cart_id']
            shop_id = parse_merchant_private_data(data)['shop_id']
        except Exception, e:
            raise Exception("Could not read merchant private data from google notification")
        
        logging.debug("\nGoogle Message Type = %s\nOrder Number = %s\nBuyer = %s\nOrder Amount = %s" % (type, order_number, buyer,order_total))
        
        try:
            cart = get_object_or_404(Cart, pk=cart_id)
            
            if not cart.is_available():
                self.cancel_order(order_number, reason="out of stock")
                cart.remove_not_available_items()
                logging.error("Order id: %s, cancel. Out of stock, Cart id: %s" %(order_number, cart.id))
                return
            
            sell = cart.close("GoogleCheckout")
            
            order = GoogleCheckoutOrder(sell=sell)
            order.buyer_id = buyer_id
            order.order_number = order_number
            order.save()
            
        except Exception, e:
            raise Exception("Processing new order exception: %s" % e)
        
    def cancel_order(self, order_id, reason="Without reason"):
        """
        Cancel an order, given the order_id provided by google checkout
        """
        msg = "Your order <%s> has been cancelled. Reason: %s" % (order_id, reason)
        self.controller().cancel_order(order_id, msg, "")
        logging.info("Order <%s> cancelled..." % order_id)
        
    def charge_order(self, order_id, amount):
        self.controller().charge_order(order_id, amount)
        logging.info("Order <%s> charged..." % order_id)
        
    def refund_order(self, order_id, amount, reason="No reason"):
        self.controller().refund_order(order_id, amount, reason)
        logging.info("Order <%s> was refunded with %s because %s..." % (order_id, amount, reason))
        
    def authorize_order(self, order_id):
        self.controller().authorize_order(order_id)
        logging.info("Order <%s> was authorized" % order_id)
        
    def process_order(self, order_id):
        self.controller().process_order(order_id)
        logging.info("Order <%s> was processed" % order_id)
        
    def deliver_order(self, order_id):
        """
        Set that the order has been shipped
        """
        self.controller().deliver_order(order_id, send_email=True)
        logging.info("Order <%s> was mark as shipped" % order_id)
        
    def unarchive_order(self, order_id):
        self.controller().unarchive_order(order_id)
        
    def archive_order(self, order_id):
        self.controller().archive_order(order_id)
        
    def add_tracking_data(self, order_id, company, tracking_number):
        self.controller.add_tracking_data(order_id, company, tracking_number)
        
        
@shop_required
def cancel(request):
    return HttpResponse()

@shop_required    
def success(request):    
    return HttpResponse()

def process_google_message(request):
    from payments.models import GoogleCheckoutShopSettings
    
    if not request.POST:
        raise Http404('Has to be a POST request')
    
    data = request.POST
    logging.info("IPN Message from google: %s" % data)
    
    #TODO: Remove this on production!
    old_orders = ["808615120118108", "321915336139579", "500070226120390", "302881105972300", "105051742211290", "576829210613310", "900431298819542", "363385014219421", "110875583474629", "219294873728709", "863418324673725", "754725166854855", "440614064042214", "363224040566596", "423067801498241", "412755410069270", "113080123162102", "948298670658337", "924912876161814", "569064450435781", "940848691218939", "210458200450508", "553564979816637", "569481707803816", "459990434049449", "244184444070541", "233130725515979", "865960480529054", "360415071672616", "338491509385444", "412304365353555", "552610308576885", "208010922301070" ]    
    if data['google-order-number'] in old_orders: 
        logging.error("old order, not will be processed...")
        return HttpResponse(notification_response(data['serial-number']))
    
    try:
        merchant_private_data = parse_merchant_private_data(data)
        shop_id = merchant_private_data['shop_id']
        shop = get_object_or_404(Shop, pk=shop_id)
    except Exception, e:
        logging.error("Error when trying to get shop instance object. Exception? %s" % e)
        return HttpResponse(status=500)
    
    try:   
        settings = GoogleCheckoutShopSettings.objects.filter(shop = shop).get()
    except GoogleCheckoutShopSettings.DoesNotExist:
        logging.error("GoogleCheckout Settings for shop %s do not exist" % shop)
        return HttpResponse(status=500)
    
    try:
        googlecheckout_gw = GoogleCheckoutGateway(settings.merchant_id, settings.merchant_key, debug=True)
        googlecheckout_gw.process_message(data)
    except Exception, e:
        logging.error("Error when trying to process google notification. Exception? %s" % e)
        return HttpResponse(status=500)
    
    response = notification_response(data['serial-number'])
    logging.debug(response)
    return HttpResponse(response)
    
def notification_response(serial_number):
    return """<notification-acknowledgment xmlns="http://checkout.google.com/schema/2" serial-number="%s"/>""" % serial_number.strip()

def parse_merchant_private_data(post):
    """
    ej : parse_merchant_private_data(request.POST)
    """
    merchant_private_data = {}
    if post.has_key('order-summary.shopping-cart.merchant-private-data'):
        elem = post['order-summary.shopping-cart.merchant-private-data']
        for pair in elem.split("#"):
            (key, value) = pair.split(":")
            merchant_private_data[key] = value
    return merchant_private_data