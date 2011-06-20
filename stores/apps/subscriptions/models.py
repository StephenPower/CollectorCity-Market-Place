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
    total_store_revenue = models.DecimalField(max_digits=11, decimal_places=2) 
    concurrent_store_items = models.PositiveIntegerField() 
    concurrent_auction_items = models.PositiveIntegerField()
    listings_per_month = models.PositiveIntegerField()
    payment_methods = models.PositiveSmallIntegerField()
    pictures_per_lot = models.PositiveSmallIntegerField(default=1)
    pictures_per_item = models.PositiveSmallIntegerField(default=1)
    admin_accounts = models.PositiveSmallIntegerField()
    total_mbs_storage = models.IntegerField(default=50)        
    auto_tax_integration = models.BooleanField(default=False)
    google_analytics_support = models.BooleanField(default=False)
    custom_migration = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    secret_code = models.CharField(max_length=255, blank=True, null=True)
    
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
        days_past_due
        discounts trial_duration
        first_billing_dateupdate
        gateway
        id
        merchant_account_id      
        number_of_billing_cycles
        paid_through_date
        payment_method_token
        plan_id
        status
        trial_duration_unit
        trial_period
        update_signature

        
            cancel
            create            
            create_signature            
            id            
            failure_count
            find
            first_billing_date            
            merchant_account_id
            next_billing_date
            payment_method_token
            plan_id
            price
            retryCharge
            search
            status            
            transactions            
            trial_duration
            trial_period
            trial_duration_unit
            update
            update_signature            
            verify_keys
            @return: [billing_period_start_date, billing_period_end_date, next_billing_date, price, transactions]
        """
        from django.conf import settings
        from payments.gateways.braintreegw import BraintreeGateway 
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        subscription = gw.get_subscription_details(self.subscription_id)
        return [
            subscription.billing_period_start_date, 
            subscription.billing_period_end_date, 
            subscription.next_billing_date, 
            subscription.price, 
            subscription.transactions,
            subscription.status,
            subscription.balance            
        ]

                
class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(Subscription)
    datetime = models.DateTimeField()
    amount = models.FloatField()
    
class SubscriptionCancelation(models.Model):
    shop = models.ForeignKey(Shop)
    subscription = models.ForeignKey(Subscription)
    date_time = models.DateTimeField(auto_now_add=True)