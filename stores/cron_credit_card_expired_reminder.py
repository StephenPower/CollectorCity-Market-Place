#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ
from django.core.mail import send_mail, EmailMessage
#from django.db import transaction

import settings
setup_environ(settings)

from shops.models import Shop

"""
This cron sends an email to those users that have their credit card expired.
It should run once a day. At the midnight
"""
def send_credit_card_expired_reminder():
    
    shops = Shop.objects.all()
    today = datetime.date.today()
    for shop in shops:
        
        try:
            billing = shop.billing_info()
            if not billing:
                msg = "Missing Billing Info Data. Shop %s has not billing info attached. Please go to admin and create one. Fill the entity with the same fields saved on braintree" % shop
                raise Exception(msg)
            
            cc = billing.credit_card()
            if not cc:
                msg = "Can't get credit card info, check if customer_id for shop %s in ShopBillingInfo is correct (not undefined)." % shop
                raise Exception(msg)
            
            expiration_date= cc['expiration_date']
            cc_type = cc['card_type']
            cc_masked = cc['masked_number']
            
            expired = False
            
            month, year = expiration_date.split("/")
            date = datetime.date(int(year), int(month), 1)
            expired = date < today
            
            if expired:
                msg = "\nWe have detected that your credit card - %s (%s) -  is expired. Please go to your Shop Admin Console and update your credit card information." % (cc_type, cc_masked)
                mail = EmailMessage(subject='Credit Card Expired',
                                    body=msg,
                                    from_email=settings.EMAIL_FROM,
                                    to=[shop.owner().email],
                                    headers={'X-SMTPAPI': '{\"category\": \"Credit Card Expired\"}'})
                mail.send(fail_silently=True)
#                send_mail('Credit Card Expired', msg, settings.EMAIL_FROM, [shop.owner().email], fail_silently=True)
                
        except Exception, e:
            logging.critical(e)
            mail = EmailMessage(subject='Error when trying to send email notifying that customer have card expired!',
                                body=e,
                                from_email=settings.EMAIL_FROM,
                                to=[mail for (name, mail) in settings.STAFF],
                                headers={'X-SMTPAPI': '{\"category\": \"Error\"}'})
            mail.send(fail_silently=True)
#            send_mail('Error when trying to send email notifying that customer have card expired!', e , settings.EMAIL_FROM, [mail for (name, mail) in settings.STAFF], fail_silently=True)


if __name__ == "__main__":
    send_credit_card_expired_reminder()