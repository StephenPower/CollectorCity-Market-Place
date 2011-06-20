from django.db import models

from picklefield import PickledObjectField
from shops.models import Shop
from sell.models import Sell, Cart


class PayPalShopSettings(models.Model):
    shop = models.ForeignKey(Shop)
    payer_id = models.CharField(max_length=92)
    email = models.EmailField()
    first_name = models.EmailField()
    last_name = models.EmailField()
    perms = PickledObjectField(default=[])

    def __unicode__(self):
        return "Paypal settings: %s" % self.shop.name


class PayPalToken(models.Model):
    """
        Model to associate a returning customer from paypal with a given sell
    """
    cart = models.ForeignKey(Cart)
    token = models.CharField(max_length=255, unique=True) #TODO: ver que tan unique es el token de paypal
    timestamp = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    

class GoogleCheckoutShopSettings(models.Model):
    shop = models.ForeignKey(Shop)
    merchant_id = models.CharField(max_length=20)
    merchant_key = models.CharField(max_length=40)
    
    def __unicode__(self):
        return "Google Checkout settings for <%s>" % self.shop.name

class PayPalTransaction(models.Model):
    sell = models.ForeignKey(Sell)
    transaction_id = models.CharField(max_length=30)
    
    def __unicode__(self):
        return "%s > %s" % (self.sell, self.transaction_id)
    
class GoogleCheckoutOrder(models.Model):
    sell = models.ForeignKey(Sell)
    order_number = models.CharField(max_length=20)
    buyer_id = models.CharField(max_length=20)
    financial_state = models.CharField(max_length=20)
    fulfillment_state = models.CharField(max_length=20)
    ready_to_ship = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "Google Checkout Order <%s>" % self.order_number
    
    def sell_charged(self):
        self.ready_to_ship = True
        self.save()
        self.sell.payment.pay()
        
        
    def sell_shipped(self):
        """
        NEW               - The order has been received but not prepared for shipping.
        PROCESSING        - The order is being prepared for shipping.
        DELIVERED         - The seller has shipped the order.
        WILL_NOT_DELIVER  - The seller will not ship the order; this status is used for canceled orders. 
        """
        pass
        
    def sell_cancelled(self):
        pass
    
    def sell_authorized(self):
        pass
    
    
class ManualPaymentShopSettings(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=50)
    description = models.TextField(default="")
    instructions = models.TextField()
    

class BraintreeShopSettings(models.Model):
    shop = models.ForeignKey(Shop)
    merchant_id = models.CharField(max_length=40)
    public_key = models.CharField(max_length=40)
    private_key = models.CharField(max_length=40)
    
    def __unicode__(self):
        return "Braintree settings for <%s>" % self.shop.name
    
class BrainTreeTransaction(models.Model):
    sell = models.ForeignKey(Sell)
    transaction_id = models.CharField(max_length=20)
    
    def __unicode__(self):
        return "%s > %s" % (self.sell, self.transaction_id)