#!/usr/bin/env python
# -*- coding: utf-8 -*-

###    This procedure must be launched once a day
###    1 2 * * * python /home/usuario/projects/YYZ/poc/cron_past_due.py >> /home/usuario/projects/YYZ/poc/test2.cron

"""
This cron is used to update the payments status of all of these sells that were paid via BrainTree gateway. 
Once a payment transaction is setted as submitted_for_settlement, i could pass one day to change to status = settled.  
"""

import os
import logging
import datetime
import decimal

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ
#from django.db import transaction

import settings
setup_environ(settings)

from payments.models import *
from payments.gateways.braintreegw import BraintreeGateway
from invoices.models import Invoice
from shops.models import Shop

def update_settled_braintree_payments():
    today = datetime.datetime.today()
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    #today = datetime.datetime(2010, 8, 25)
    gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
    transactions = gw.get_daily_transactions(yesterday)
    logging.info("%s transactions were found yesterday %s" % (len(transactions), yesterday))
    for transaction in transactions:
        
        if gw.is_settled(transaction.id):
            logging.info("Transaction ID=%s was SETTLED! Updating the associated sell instance..." % transaction.id)
            try:
                btx = BrainTreeTransaction.objects.filter(transaction_id=transaction.id).get()
                if btx.sell.payment.state_actual.state != "PA":
                    btx.sell.payment.pay()
                    logging.info("%s was marked as paid..." % btx.sell)
                else:
                    logging.info("%s was already marked as paid, nothing to do..." % btx.sell)
            except BrainTreeTransaction.DoesNotExist:
                logging.critical("Transaction ID=%s is not associated to any Sell!!" % transaction.id)
            
        elif gw.is_submitted_for_settlement(transaction.id):
            logging.info("Transaction ID=%s is SUBMITTED_FOR_SETTLEMENT yet! Nothing to do, wait to status change to SETTLED" % transaction.id)
            logging.info("Check how long is in this situation... do something if several days have passed")
        
        elif gw.is_authorized(transaction.id):
            logging.info("Transaction ID=%s is AUTHORIZED! This should not be never happend because we programatically set the transaction to be submitted_for_settlement" % transaction.id)
            
        else:
            logging.info("Transaction ID=%s has status = %s" % (transaction.id, transaction.status))
            try:
                btx = BrainTreeTransaction.objects.filter(transaction_id=transaction.id).get()
                btx.sell.payment.pay()
            except BrainTreeTransaction.DoesNotExist:
                logging.critical("Transaction ID=%s is not associated to any Sell!!" % transaction.id)
        
if __name__ == "__main__":
    update_settled_braintree_payments()