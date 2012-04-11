#!/usr/bin/env python
# -*- coding: utf-8 -*-

###    This procedure must be launched once a day
###    1 2 * * * python /home/usuario/projects/YYZ/poc/cron_past_due.py >> /home/usuario/projects/YYZ/poc/test2.cron

import os
import logging
import datetime
import decimal

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ
from django.core.mail import send_mail, EmailMessage
#from django.db import transaction

import settings
setup_environ(settings)

from payments.gateways.braintreegw import BraintreeGateway
from invoices.models import Invoice
from shops.models import Shop

def send_daily_invoice_notification():
    today = datetime.datetime.today()
    #today = datetime.datetime(2010, 7, 15)
    gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
    transactions = gw.get_daily_transactions(today)
    logging.info("%s transactions were found today %s" % (len(transactions), today))
    for transaction in transactions:
        if transaction.subscription_id is not None:
            invoice = Invoice()
            
            invoice.cc_mask = '*'*12 + transaction.credit_card_details.masked_number[12:]
            invoice.cc_type = transaction.credit_card_details.card_type 
            invoice.charge =  decimal.Decimal(transaction.amount)
            invoice.currency = transaction.currency_iso_code        
            invoice.transaction_status_response = transaction.processor_response_text
            invoice.transaction_type = transaction.type.lower()
            invoice.transaction_id = transaction.id
            
            invoice.customer_name = "%s %s" % (transaction.customer_details.first_name, transaction.customer_details.last_name)
            invoice.customer_email = transaction.customer_details.email
            invoice.customer_id = transaction.customer_details.id
            invoice.shop_dns =  "<Unspecified Shop>" if transaction.customer_details.website is None else transaction.customer_details.website
            try:
                shop_id = None if transaction.vault_customer.custom_fields is '' else transaction.vault_customer.custom_fields.get("shop_id", None)
                if shop_id is not None: 
                    try:
                        shop = Shop.objects.get(id=shop_id)
                        invoice.shop = shop
                        invoice.market_place = shop.marketplace.name
                    except Shop.DoesNotExist:
                        logging.error("Shop ID = %s not exist for user %s" % (shop_id, invoice.customer_name))
                        pass
                else:
                    logging.error("User %s has not setted shop_id property in braintree" % invoice.customer_name)
                
            except Exception, e:
                logging.error(e)
                pass
            
            
            invoice.subscription_id = transaction.subscription_id
            subscription = gw.get_subscription_details(invoice.subscription_id)
            
            invoice.plan_id = subscription.plan_id
            invoice.valid_from = subscription.billing_period_start_date
            invoice.valid_up_to = subscription.billing_period_end_date
            invoice.next_billing_date = subscription.next_billing_date
            
            invoice.save()
            msg = invoice.to_text()
            
            logging.info("Sending email to %s. tx=%s, charge=%s, " % (invoice.customer_name, invoice.transaction_id, invoice.charge))
            mail = EmailMessage(subject='%s | Notification Invoice' % invoice.market_place,
                                body=msg,
                                from_email=settings.EMAIL_FROM,
                                to=[invoice.customer_email]+[mail for name, mail in settings.STAFF],
                                headers={'X-SMTPAPI': '{\"category\": \"Notification Invoice\"}'})
            mail.send(fail_silently=True)
            #        send_mail('%s | Notification Invoice' % invoice.market_place, msg, settings.EMAIL_FROM, [invoice.customer_email]+[mail for name, mail in settings.STAFF], fail_silently=True)


if __name__ == "__main__":
    send_daily_invoice_notification()