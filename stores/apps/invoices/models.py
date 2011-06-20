import datetime

from django.db import models

from django.utils.translation import ugettext_lazy as _

from shops.models import Shop

TRANSACTION_TYPE = (("sale", "SALE"), ("credit", "CREDIT"), ("refund", "REFUND"))

class Invoice(models.Model):
    market_place = models.CharField(max_length=100)
    shop = models.ForeignKey(Shop, null=True)
    shop_dns = models.CharField(max_length=200)
    
    cc_mask = models.CharField(max_length=20)
    cc_type = models.CharField(max_length=40) 
    charge =  models.DecimalField(max_digits=11, decimal_places=2)
    currency = models.CharField(max_length=5)
    
    transaction_status_response = models.CharField(max_length=200)  
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=40)
    transaction_id = models.CharField(max_length=100)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=200)
    
    subscription_id = models.CharField(max_length=200)
    
    plan_id = models.CharField(max_length=40)
    valid_from = models.DateTimeField()
    valid_up_to = models.DateTimeField()
    next_billing_date = models.DateTimeField()
    
    creation_date = models.DateTimeField(auto_now_add=True)
    last_send = models.DateTimeField(null=True)
    
    def to_text(self):
        text = """
        ------------------------INVOICE %s Transaction ID: %s -----------------------
                
        This is an INVOICE for your shop %s. 1 month %s Plan %s %s From %s to %s.
        
        Transaction Type   : %s
        Transaction Status : %s
        Bill to            : %s
        Credit Card Type   : %s
        Credit Card Billed : %s 
        Charge             : %s %s        
        
        This charge covers your account until %s. You will be billed again at %s        
    
        ---------------------------------------------------------------------------------------------------------        
        Thank you for using %s.
        
        """ % (datetime.datetime.today(), self.transaction_id, self.shop_dns, self.plan_id, self.currency, self.charge, 
               self.valid_from, self.valid_up_to, self.transaction_type, self.transaction_status_response, 
               self.customer_name, self.cc_type, self.cc_mask, self.currency,
               self.charge, self.valid_up_to, self.next_billing_date, self.market_place)  
        
        return text
                
    
    