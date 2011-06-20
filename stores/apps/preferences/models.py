import decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.models import USStateField

from shops.models import Shop


DAYS = [
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ] 

    
class Preference(models.Model):
    shop = models.ForeignKey(Shop)
    name_store = models.CharField(max_length=60, help_text="The Name of your Store")
    email = models.EmailField(help_text="Email address when signed up")
    phone = models.CharField(max_length=60)
    taxes_same_state_store = models.BooleanField() 
    taxes_to_shipping_fees = models.BooleanField()
    checkout_currency = models.CharField(max_length=60, default = "USD") 
    allow_sessions = models.BooleanField()
    allow_open_auctions = models.BooleanField()
    default_days = models.CharField(max_length=1, choices=DAYS, default=5)
    open_auto_extend = models.BooleanField(default = True)
    session_auto_extend = models.BooleanField(default = True)
    google_analytics_account_number = models.CharField(max_length=30, default = "")
   
    @classmethod
    def get_preference(cls, shop):
        try:
            preference = Preference.objects.filter(shop=shop).get()
        except:
            preference = Preference(shop=shop)
            preference.save()
        return preference

    def __str__(self):
        return "%s <%s> Preferences" % (self.shop, self.shop.default_dns)

class ShippingWeight(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    from_weight = models.DecimalField(max_digits=11, decimal_places=2)
    to_weight = models.DecimalField(max_digits=11, decimal_places=2)
    
    @classmethod
    def calculate_charge(cls, shop, total_weight):
        options = ShippingWeight.objects.filter(shop=shop)
        for option in options:
            if option.match(total_weight):
                return option.price
            #logging.debug("Option %s not watch and not will be aplied" % option)
        return decimal.Decimal(0)
    
    def match(self, weight):
        return (weight >= self.from_weight and weight <= self.to_weight)

    def __str__(self):
        return "%s <%s-%s> cost: %s" % (self.shop, self.from_weight, self.to_weight, self.price)
    
class ShippingPrice(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    from_price = models.DecimalField(max_digits=11, decimal_places=2)
    to_price = models.DecimalField(max_digits=11, decimal_places=2)
    
    @classmethod
    def calculate_charge(cls, shop, total_price):
        options = ShippingPrice.objects.filter(shop=shop)
        for option in options:
            if option.match(total_price):
                return option.price
            #logging.debug("Option %s not watch and not will be aplied" % option)
        return decimal.Decimal(0)
    
    def match(self, price):
        return (price >= self.from_price and price <= self.to_price)
    
    def __str__(self):
        return "%s <%s-%s> cost: %s" % (self.shop, self.from_price, self.to_price, self.price)
    
class ShippingItem(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    from_item = models.IntegerField()
    to_item = models.IntegerField()
    
    def __str__(self):
        return "%s <%s-%s> cost: %s)" % (self.shop, self.from_item, self.to_item, self.price)
    
    @classmethod
    def calculate_charge(cls, shop, total_items):
        options = ShippingItem.objects.filter(shop=shop)
        for option in options:
            if option.match(total_items):
                return option.price
            #logging.debug("Option %s not watch and not will be aplied" % option)
        return decimal.Decimal(0)
    
    def match(self, items):
        return (items >= self.from_item and items <= self.to_item)

    
class TaxState(models.Model):
    shop = models.ForeignKey(Shop)
    state = USStateField()
    tax = models.DecimalField(max_digits=11, decimal_places=2)
    apply_tax_to_shipping = models.BooleanField(default=False)

    def __str__(self):
        return "%s > %s: $%s (apply_on_ship=%s)" % (self.shop, self.state, self.tax, self.apply_tax_to_shipping)
    
class DnsShop(models.Model):
    shop = models.ForeignKey(Shop)
    dns = models.CharField(max_length=255)
    default = models.BooleanField(default=False)
    
    
TYPE_NOTIFICATION=[
                   ('OC',_('Order confirmation')),
                   ('AWC',_('Auction Won Confirmation')),
                   ('NON',_('New Order Notification')),
                   ('CB',_('Contact Buyer')),
#                   ('SU',_('Shipping Update')),
#                   ('SC',_('Shipping Confirmation')),
                   ]

class EmailNotification(models.Model):
    shop = models.ForeignKey(Shop)
    type_notification = models.CharField(max_length=3, choices=TYPE_NOTIFICATION)
    subject = models.CharField(max_length=60)     
    body = models.TextField()
    
class ShopPolicies(models.Model):
    shop = models.ForeignKey(Shop)
    refund_policy = models.TextField()
    privacy_policy = models.TextField()
    terms_of_service = models.TextField()
    def __unicode__(self):
        return "%s shop Policies" % self.shop