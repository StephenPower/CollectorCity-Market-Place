import decimal
import logging

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from auth.models import User
from shops.models import Shop
from for_sale.models import Item

class SellError(Exception):
    pass

class ShippingData(models.Model):
    street_address = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    zip = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    
    def __str__(self):
        return "%s, %s, %s, %s" % (self.street_address, self.city, self.state, self.country)


class Cart(models.Model):
    bidder = models.ForeignKey(User)
    shop = models.ForeignKey(Shop)
    shippingdata = models.OneToOneField(ShippingData, null=True, blank=True)
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.bidder)
    
    def close(self, payment_method):
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template import Context, Template
        from preferences.models import EmailNotification        
        
        if self.shippingdata is None: raise Exception("Cart Shipping address should never be empty. Something is wrong!")
        sell = Sell.new_sell(self.shop, self.bidder, self.shippingdata, self)
        items = []
        for cart_item in self.cartitem_set.all():
            sell_item = SellItem(sell=sell, product=cart_item.product, qty=cart_item.qty, price=cart_item.price)
            sell_item.save()
            
            item = {'title': sell_item.product.title, 'qty': sell_item.qty, 'price': sell_item.price, 'total': sell_item.get_total()}
            items.append(item)
            
            cart_item.delete()
            
        sell.payment_method = payment_method
        sell.save() 
        
        #Why is this put to None!!!
        self.shippingdata = None
        self.save()
        
        # -----------------------------
        # Send notification to Shop that new order has been created
        c = Context({
                'buyer_name': self.bidder.get_full_name(),
                'buyer_email': self.bidder.email,
                'gateway': sell.payment_method,
                'shop': self.shop,
                'shipping_street_address': sell.shippingdata.street_address,
                'shipping_city': sell.shippingdata.city,
                'shipping_state': sell.shippingdata.state,
                'shipping_zip': sell.shippingdata.zip,
                'shipping_country': sell.shippingdata.country,
                'sell_date' : sell.date_time,
                'sell_total' : sell.total,
                'sell_without_taxes': sell.total_without_taxes,
                'sell_total_taxes': sell.total_taxes,
                'sell_total_shipping': sell.total_shipping,
                'items': items
            })
        
        # SEND NEW ORDER NOTIFICATION TO SHOP OWNER       
        try:
            notification = EmailNotification.objects.filter(type_notification='NON', shop=self.shop).get()
            subj_template = Template(notification.subject)
            body_template = Template(notification.body)
            
            subj_text = subj_template.render(c)
            body_text = body_template.render(c)
            send_mail(subj_text, body_text, settings.EMAIL_FROM,  [self.shop.admin.email], fail_silently=True)
            
        except EmailNotification.DoesNotExist:
            msg = "New Order Notification"
            send_mail("New order has been generated!", msg, settings.EMAIL_FROM,  [self.bidder.email], fail_silently=True)
            
        except Exception, e:
            send_mail("Fail when trying to send email!", "%s" % e, settings.EMAIL_FROM,  [mail for (name, mail) in settings.STAFF], fail_silently=True)
        
        # SEND NEW ORDER NOTIFICATION TO CUSTOMER
        try:
            notification = EmailNotification.objects.filter(type_notification='OC', shop=self.shop).get()
            subj_template = Template(notification.subject)
            body_template = Template(notification.body)
            
            subj_text = subj_template.render(c)
            body_text = body_template.render(c)
            send_mail(subj_text, body_text, settings.EMAIL_FROM,  [self.bidder.email], fail_silently=True)
            
        except EmailNotification.DoesNotExist:
            msg = "This mail is to confirm your order on %s" % self.shop
            send_mail("New order has been generated!", msg, settings.EMAIL_FROM, [self.bidder.email], fail_silently=True)
            
        except Exception, e:
            from django.conf import settings
            send_mail("Fail when trying to send email!", "%s" % e, settings.EMAIL_FROM,  [mail for (name, mail) in settings.STAFF], fail_silently=True)
        
        return sell
    
    def add(self, product, price, qty=1):
        try:
            product_type = ContentType.objects.get_for_model(product)
            cart_item = CartItem.objects.filter(object_id=product.id, content_type__pk=product_type.id).get()
            cart_item.qty += qty
        except CartItem.DoesNotExist:
            cart_item = CartItem(cart=self, product=product, price=price, qty=qty)
        product.decrease_qty(qty)
        cart_item.save()

    def remove(self, cartitem):
        """ Remove an item from the cart """
        try:
            cartitem.product.increase_qty(cartitem.qty)
            cartitem.delete()
        except CartItem.DoesNotExist:
            pass
    
    def remove_one(self, cartitem):
        """ Remove just one item from the cart """
        try:
            cartitem.product.increase_qty(1)
            if cartitem.qty == 1:
                cartitem.delete()
            else:
                cartitem.qty -= 1
                cartitem.save()
        except CartItem.DoesNotExist:
            pass
        
    def clean(self):
        """ Clean the cart """
        for cartitem in self.cartitem_set.all():
            self.remove(cartitem)
                
    def total(self):
        """
            Get back the total prize without any taxes or shipping cost
        """
        price = decimal.Decimal('0.00')
        for item in self.cartitem_set.all():
            price += item.price * item.qty
        return decimal.Decimal(price)
    
    def total_weight(self):
        """
            Get back the total weight of the cart
        """
        weight = 0
        for item in self.cartitem_set.all():
            weight += item.product.weight * item.qty
        return weight
    
    def total_items(self):
        """
            Return total amount of items in the cart
        """
        items = 0
        for item in self.cartitem_set.all():
            items += item.qty
        return items
    
    def taxes(self):
        """
            Return taxes for the shipping address
        """
        return self.rate_taxes() * self.total()
    
    def rate_taxes(self):
        """
            Return the rate that should be aplied to to this cart according to where is going to be shipped  
        """
        from payments.taxes import TaxCalculator
        return TaxCalculator.get_tax(shop=self.shop, state=self.shippingdata.state, city=self.shippingdata.city)
        
    
    def shipping_charge(self):
        """
            Return the cost of shipping this cart
        """
        from payments.shipping import ShippingCalculator
        return ShippingCalculator.get_charge(self)
            
    def total_with_taxes(self):
        """
            Return total amount due with taxes calculated for the shipping address
        """    
        return self.total() + self.taxes() + self.shipping_charge()
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart)
    
    price = models.DecimalField(max_digits=11, decimal_places=2) 
    qty = models.IntegerField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')
    
    def sub_total(self):        
        return self.price * self.qty

#TODO: Remove the null=True properties in shop & bidder!!!
class Sell(models.Model):
    payment_method = models.CharField(max_length=255, default="Manual Payment")
    date_time = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(User, null=True)
    shop = models.ForeignKey(Shop, null=True)
    closed = models.BooleanField(default = False)
    shippingdata = models.OneToOneField(ShippingData, null=True, blank=True)
    total = models.DecimalField(max_digits=11, 
                                decimal_places=2, default=decimal.Decimal(0))
    total_without_taxes = models.DecimalField(max_digits=11, 
                                decimal_places=2, default=decimal.Decimal(0))
    total_taxes = models.DecimalField(max_digits=11, 
                                decimal_places=2, default=decimal.Decimal(0))
    total_shipping = models.DecimalField(max_digits=11, 
                                decimal_places=2, default=decimal.Decimal(0))
    cancel = models.BooleanField(default = False)
    #TODO: Shipping charge, Taxes and Total Cost should be properties, not a calculated value...
    #TODO: don't should add billingdata to?
    def __unicode__(self):
        return "%s > %s (ID=%s)" % (self.shop, self.bidder, self.id)
    
    @classmethod
    def new_sell(cls, shop, bidder, shippingdata, cart):
        sell = Sell(bidder=bidder, shop=shop, shippingdata=shippingdata)
        sell.total_without_taxes = cart.total()
        sell.total = cart.total_with_taxes()        
        sell.total_shipping = cart.shipping_charge()
        sell.total_taxes = cart.taxes()
        sell.save()
        Payment.new_pending_payment(shop, sell)
        Shipping.new_pending_shipping(shop, sell)
        return sell
    
    def is_manual_payment(self):
        return 'Manual Payment' in self.payment_method

    def is_paypal_payment(self):
        return self.payment_method == 'PayPal'

    def is_google_checkout(self):
        return self.payment_method == 'GoogleCheckout'

    def is_braintree(self):
        return self.payment_method == 'BrainTree'

    
    def get_payment(self):
        return self.payment_set.all()[0]

#    def _total_without_taxes(self):
#        result = 0
#        for item in self.sellitem_set.all():
#            result += item.price * item.qty
#        return result   
#
#    def _taxes(self):
#        """
#            Return taxes for the shipping address
#        """
#        from payments.taxes import TaxCalculator
#        taxes = TaxCalculator.get_tax(shop=self.shop, state=self.shippingdata.state, city=self.shippingdata.city)
#        return taxes * self.total_without_taxes()
#    
#    def _total(self):
#        """
#            Return total amount due with taxes calculated for the shipping address
#        """
#        return self._total_without_taxes() + self._taxes()
    

    def close(self):
        self.closed = True
        self.save()
        
    def open(self):
        self.closed = False
        self.save()
        
    def cancel_sell(self):
        if self.payment.state_actual.state != 'PA':
            for item in self.sellitem_set.all():
                item.product.increase_qty(item.qty)
                item.product.activate()
                item.save()
            self.cancel = True
            self.save()
        else:
            raise SellError('Can not cancel this sell, your state is paid.')
        
    def refund(self):
        if self.payment.state_actual.state == 'PA':
            if self.is_manual_payment():
                pass
            if self.is_paypal_payment():
                from payments.gateways.paypal import PayPalGateway
                from payments.models import PayPalShopSettings, PayPalTransaction
                
                paypal_gw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                                          password=settings.PAYPAL_PASSWORD,
                                          sign=settings.PAYPAL_SIGNATURE,
                                          debug=settings.PAYPAL_DEBUG)
                                
                try:
                    txn = PayPalTransaction.objects.filter(sell=self).get()
                    paypal_gw.RefundTransaction(txn.transaction_id, 'Full', 'USD', self.total, "Programatic refund from shop admin")
                except PayPalTransaction.DoesNotExist:
                    raise SellError("PayPalTransaction not found. Refund can't be performed...")
                
                    
            if self.is_google_checkout():
                from payments.gateways.googlecheckout import GoogleCheckoutGateway, GoogleCheckoutOrder
                from payments.models import GoogleCheckoutShopSettings
                
                try:
                    google_settings = GoogleCheckoutShopSettings.objects.filter(shop = self.shop).get()
                except GoogleCheckoutShopSettings.DoesNotExist:
                    raise SellError("Google Checkout Settings are disabled! Refund can't be performed")
                    
                googlecheckout_gw = GoogleCheckoutGateway(google_settings.merchant_id, 
                                                          google_settings.merchant_key, 
                                                          debug=True)
                try:
                    order = GoogleCheckoutOrder.objects.filter(sell=self).get()
                    refund = googlecheckout_gw.refund_order(order.order_number, self.total, "Programatic refund from shop admin")
                except GoogleCheckoutOrder.DoesNotExist:
                    raise SellError("This sell it's not associated to any GoogleCheckoutOrder! Refund can't be performed")
                
                
            if self.is_braintree():
            
                from payments.gateways.braintreegw import BraintreeGateway
                from payments.models import BrainTreeTransaction
                
                try:
                    bt_txn = BrainTreeTransaction.objects.filter(sell=self).get()
                except BrainTreeTransaction.DoesNotExist:
                    raise SellError('There is no Braintree transaction associated to this sell!')
                
                gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
                refund = gw.refund_transaction(bt_txn.transaction_id)
                if not refund.is_success:
                    message = ""
                    if refund.transaction:
                        code = refund.transaction.processor_response_code
                        text = refund.transaction.processor_response_text
                        message = "Refund Failed! %s.\[%s] %s" % (refund.message, code, text)
                        
                    else:
                        for error in refund.errors.deep_errors:
                            txt = "attribute: %s, code: %s. %s" (error.attribute, error.code, error.message)    
                            message += txt + "\n"
                    raise SellError("Can't do refund. %s" % message)    
                
                
            for item in self.sellitem_set.all():
                item.product.increase_qty(item.qty)
                item.product.activate()
                item.save()
            self.cancel = True
            self.save()
            self.payment.refunded()
        else:
            raise SellError('Can not refund this sell, your state is not paid.')
            
    
class SellItem(models.Model):
    sell = models.ForeignKey(Sell)
    price = models.DecimalField(max_digits=11, 
                                decimal_places=2) 
    qty = models.IntegerField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return "Item : %s" % self.product
    
    def get_total(self):
        return "%0.2f" % (self.price * self.qty)
    
    
   
STATE_PAYMENT = [
    ('PE', _('Pending')),
    ('PA', _('Paid')),
    ('FA', _('Failed')),
    ('RE', _('Refunded')),
]   

class Payment(models.Model):
    shop = models.ForeignKey(Shop)
    sell = models.OneToOneField(Sell)
    total = models.DecimalField(max_digits=11, decimal_places=2, default=decimal.Decimal("0.0"))
    state_actual = models.OneToOneField('PaymentHistory', null=True, related_name="payment_history")
    def __unicode__(self):
        return "%s - Sell<%s> $%s (%s)" % (self.shop, self.sell.id, self.total, self.state_actual)
    
    #TODO: transaction in this methods
    @classmethod
    def new_pending_payment(cls, shop, sell):
        payment = Payment(shop=shop, sell=sell)
        payment.save()
        payment_history = PaymentHistory(payment=payment, state="PE")
        payment_history.save()
        payment.state_actual = payment_history 
        payment.save()
        
    def pay(self):
        payment_history = PaymentHistory(payment=self, state="PA")
        payment_history.save()
        self.state_actual = payment_history
        self.total = self.sell.total
        self.save() 
    
    def fail(self):
        payment_history = PaymentHistory(payment=self, state="FA")
        payment_history.save()
        self.state_actual = payment_history
        self.save()     

    def refunded(self):
        payment_history = PaymentHistory(payment=self, state="RE")
        payment_history.save()
        self.state_actual = payment_history
        self.save()     

    
    
class PaymentHistory(models.Model):
    payment = models.ForeignKey(Payment)
    date_time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=STATE_PAYMENT)
    def __unicode__(self):
        return self.state
    
STATE_SHIPPING = [
    ('PE', _('Pending')),    
    ('DI', _('Dispatched')),
    ('FU', _('Fulfilled')),        
]


SHIPPING_SERVICES = [
    ('Amazon', _('Amazon Services')),                     
    ('Shipwire', _('Shipwire Services')),
    ('Webgistix', _('WebGistics')),
    ('Other', _('Other')),
]

class Shipping(models.Model):
    shop = models.ForeignKey(Shop)
    sell = models.OneToOneField(Sell)
    shipping_service = models.CharField(max_length=255, choices=SHIPPING_SERVICES, default='Other')
    tracking_number = models.CharField(max_length=255, default="--")
    state_actual = models.OneToOneField('ShippingHistory', null=True, related_name="shipping_history")
    def __unicode__(self):
        return "%s (%s)" % (self.sell, self.state_actual)
    
    #TODO: transaction in this methods
    @classmethod
    def new_pending_shipping(cls, shop, sell):
        shipping = Shipping(shop=shop, sell=sell)
        shipping.save()
        shipping_history = ShippingHistory(shipping=shipping, state="PE")
        shipping_history.save()
        shipping.state_actual = shipping_history 
        shipping.save()        
     
    def dispatched(self):
        shipping_history = ShippingHistory(shipping=self, state="DI")
        shipping_history.save()
        self.state_actual = shipping_history
        self.save() 

    def fulfilled(self):
        shipping_history = ShippingHistory(shipping=self, state="FU")
        shipping_history.save()
        self.state_actual = shipping_history
        self.save() 
    
    
class ShippingHistory(models.Model):
    shipping = models.ForeignKey(Shipping)
    date_time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=STATE_SHIPPING)
    def __unicode__(self):
        return self.state
    
decimal.getcontext().prec = 5
