import logging

from django.db import models 
from django.utils.translation import ugettext_lazy as _

from users.models import Profile
from market.models import MarketPlace
from shops.models import Shop

SUBSCRIPTION_STATUS = [
    ('A', _('Active')),    
    ('I', _('Inactive')),
    ('C', _('Canceled')),
]

    
#This class is a singleton & must be created only for the admin
class SubscriptionPlan(models.Model):
    #This properties should have the same values than the braintree plans
    marketplace = models.ForeignKey(MarketPlace) 
    plan_id = models.CharField(max_length=100) #Is the Plan ID field filled by plan creator
    name = models.CharField(max_length=255)
    description = models.TextField()
    trial_period = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    billing_period = models.PositiveSmallIntegerField(blank=True, default=1)
    
    #Plan Features
    total_store_revenue = models.DecimalField(max_digits=11, decimal_places=2, default=1000)
    concurrent_store_items = models.PositiveIntegerField(default=100) 
    concurrent_auction_items = models.PositiveIntegerField(default=100)
    listings_per_month = models.PositiveIntegerField(default=30)
    payment_methods = models.PositiveSmallIntegerField(default=4)
    additional_payment_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    pictures_per_lot = models.PositiveSmallIntegerField(default=1)
    pictures_per_item = models.PositiveSmallIntegerField(default=1)
    #Storage features
    total_mbs_storage = models.IntegerField(default=50)        
    total_data_transfer = models.IntegerField(default=50)
    #General Features
    admin_accounts = models.PositiveSmallIntegerField(default=1)
    auto_tax_integration = models.BooleanField(default=False)
    custom_migration = models.BooleanField(default=False)
    custom_domain_name_fee = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #Fee
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    secret_code = models.CharField(max_length=255, blank=True, null=True)
    theme_change = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #One Time
    add_new_pages = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #One Time
    #Support features
    community_support_in_forums = models.BooleanField(default=True) #Yes
    voice_support_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #Per Incident
    email_support_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #Per incident
    online_help_center = models.BooleanField(default=True) #Yes 
    #Marketing features
    google_analytics_support = models.BooleanField(default=False)
    community_wish_list = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #One Time Fee
    collect_emails = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #One Time Fee
    shopping_cart = models.BooleanField(default=True) #Yes
    create_auctions = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #One Time Fee
    show_attendance = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #Per Show
    #Shipping features
    customizable_shipping_rates = models.PositiveSmallIntegerField(default=1) #Amount of methods
    additional_shipping_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0) #Per Shipping Rate
    #Admin logins grandfather, date for effect (future), sandbox testing, ability to model revenue based on current subscriber base.??
     
    def delete(self):
        self.active = False
        self.save()
        for subscription in self.subscription_set.all():
            subscription.status = 'I'
            subscription.save()
        
    
    def __unicode__(self):
        return "%s > %s <%s> (%s)" % (self.marketplace, self.name, self.plan_id, "ACTIVE" if self.active else "INACTIVE")
    
    def has_trial_period(self):
        return self.trial_period != 0
    
    def get_limit(self, key):
        """ Return the plan limit for an specific attribute """
        try:
            value = getattr(self, key)
            return value
        except AttributeError:
            logging.critical("SubscriptionPlan instance have not %s attribute" % key)
        
class Subscription(models.Model):
    owner = models.ForeignKey(Profile)
    subscription_id = models.CharField(max_length=6) #This ID is the id returned by braintree when executes create_subcription. It suppose to return a 4-character alphanumeric ID
    plan = models.ForeignKey(SubscriptionPlan)
    status = models.CharField(max_length=1,choices=SUBSCRIPTION_STATUS, default='A')
    date_time = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """ This is done to get updated the shop.active property """
        super(Subscription, self).save(*args, **kwargs)
        shop = Shop.objects.all().filter(admin=self.owner.user).get()
        shop.save()
        
    def __str__(self):
        return "%s (Status=%s, Plan=%s)" % (self.owner.user, self.status, self.plan.name)
         
    def delete(self):
        """ Set ths Subscription Status as inactive! Shop Site will not be accesible """
        self.status = 'I'
        self.save()
    
    def get_status(self):
        for (a,b) in SUBSCRIPTION_STATUS:
            if self.status == a: return b
        return "unknown"
     
    def first_bill_date(self):
        pass
    
    def next_bill_date(self):
        pass
    
    def is_active(self):
        return self.status == "A"
        
    def extra_data(self):
        """ 
        This function uses the gateway to get additional information stored in braintree servers 
        
        Subscription object
        ---------------------
        add_ons
        balance
        billing_day_of_month
        billing_period_end_date   
        billing_period_start_date price
        cancel
        create            
        create_signature
        days_past_due
        discounts trial_duration
        failure_count
        find        
        first_billing_date
        gateway
        id
        merchant_account_id      
        number_of_billing_cycles
        next_billing_date
        paid_through_date
        payment_method_token
        plan_id
        price
        status
        retryCharge
        transactions
        trial_duration_unit
        trial_period
        trial_duration        
        update_signature
        verify_keys
        
        @return: [billing_period_start_date, billing_period_end_date, next_billing_date, price, transactions]
        """
        from django.conf import settings
        from payments.gateways.braintreegw import BraintreeGateway 
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        subscription = gw.get_subscription_details(self.subscription_id)
        return [
            subscription.billing_period_start_date, #0 
            subscription.billing_period_end_date,   #1
            subscription.next_billing_date,         #2
            subscription.price,                     #3
            subscription.transactions,              #4
            subscription.status,                    #5
            subscription.balance,                   #6
            subscription.payment_method_token,      #7     
            subscription.transactions,              #8
        ]

                
class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(Subscription)
    datetime = models.DateTimeField()
    amount = models.FloatField()
    
class SubscriptionCancelation(models.Model):
    shop = models.ForeignKey(Shop)
    subscription = models.ForeignKey(Subscription)
    date_time = models.DateTimeField(auto_now_add=True)
    
class Feature(models.Model):
    shop = models.ForeignKey(Shop)
    auctions = models.BooleanField()
    wishlist = models.BooleanField()
    mailinglist = models.BooleanField()
    google_analytics = models.BooleanField()
    show_attendance = models.BooleanField()
    custom_dns = models.BooleanField()
    paypal = models.BooleanField(default=False)
    google_checkout = models.BooleanField(default=False)
    credit_card = models.BooleanField(default=False)
    manual_payment = models.BooleanField(default=False)
    theme_change = models.BooleanField(default=False)
    add_new_pages = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s features" % self.shop
    
class FeaturePayment(models.Model):
    shop = models.ForeignKey(Shop)
    transaction_id = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    feature = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s > %s" % (self.shop, self.feature)
    
class FeaturesManager():
    
    @classmethod
    def get_feature_description(cls, feature):
        
        if feature == "auctions":
            return ("Auctions", "Auctions give your customers the capability to purchase products via lots ...")
        elif feature == "wishlist":
            return ("Wish List", "Wish List feature lets you to contact with user's special wish.")
        elif feature == "mailinglist":
            return ("Collect Mailing List", "This feature lets you collect email from your customers for creating newsletter (per ex.).")
        elif feature == "google_analytics":
            return ("Google Analytics", "This feature lets you to track your site")
        elif feature == "show_attendance":
            return ("Show Listing", "This feature allows your customers to know where you will be.")
        elif feature == "custom_dns":
            return ("Custom DNS", "Lets you customize your domain.")
        elif feature == "credit_card":
            return ("Credit Cards","This feature lets your customers to pay with their credits card.")
        elif feature == "paypal":
            return ("PayPal","This feature enables the paypal gateway and lets your customers to pay with one of the most famous online payment gateway.")
        elif feature == "google_checkout":
            return ("Google Checkout","This feature allows your customer to pay with the online payment processing service provided by Google aimed at simplifying the process of paying for online purchases.")
        elif feature == "manual_payment":
            return ("Manual Payments","This feature allow your customers to pay you manually.")
        elif feature == "theme_change":
            return ("Theme Change","This feature allows you to change the theme of your shop whenever you want.")
        elif feature == "voice_support":
            return ("Voice Support","...")
        elif feature == "email_support":
            return ("Email Support","...")
        elif feature == "add_pages":
            return ("Add New Pages","This feature allows you to add new pages to your site and customize as you want")
        return ("Unknown Feature", "")
        
    @classmethod
    def get_feature_price(cls, shop, feature):
        
        if feature == "auctions":
            return shop.auctions_feature_price()
        elif feature == "wishlist":
            return shop.wishlist_feature_price()
        elif feature == "mailinglist":
            return shop.mailinglist_feature_price()
        elif feature == "google_analytics":
            return shop.analytics_feature_price()
        elif feature == "show_attendance":
            return shop.shows_feature_price()
        elif feature == "custom_dns":
            return shop.dns_feature_price()    
        elif feature == "theme_change":
            return shop.theme_change_feature_price()
        elif feature == "voice_support":
            return shop.voice_support_price()
        elif feature == "email_support":
            return shop.email_support_price()
        elif feature == "add_pages":
            return shop.add_pages_feature_price()
        elif feature in ["credit_card", "paypal","google_checkout", "manual_payment"]:
            return shop.additional_payment_feature_price()
        
        return "0.0"
    
    @classmethod
    def set_feature_enabled(cls, shop, feature):
        shop_features = shop.get_features()
        
        if feature == "auctions":
            shop_features.auctions = True
        elif feature == "wishlist":
            shop_features.wishlist = True
        elif feature == "mailinglist":
            shop_features.mailinglist = True
        elif feature == "google_analytics":
            shop_features.google_analytics = True
        elif feature == "show_attendance":
            shop_features.show_attendance = True        
        elif feature == "custom_dns":
            shop_features.custom_dns = True
        elif feature == "paypal":
            shop_features.paypal = True
        elif feature == "google_checkout":
            shop_features.google_checkout = True
        elif feature == "credit_card":
            shop_features.credit_card = True    
        elif feature == "manual_payment":
            shop_features.manual_payment = True
        elif feature == "theme_change":
            shop_features.theme_change = True
        elif feature == "add_pages":
            shop_features.add_new_pages = True
        shop_features.save()
        