#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import datetime
import decimal

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ
from django.core.mail import send_mail
#from django.db import transaction

import settings
setup_environ(settings)

from payments.gateways.braintreegw import BraintreeGateway
from subscriptions.models import Subscription

"""
This cron sends an email with all those transactions performed today, ordered by status (declined, failed, settled....)
"""
def send_daily_transactions_notifications():
    gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
    today = datetime.datetime.today()
    transactions = gw.get_transactions(today)
    try:
        msg = "This a daily transaction summary [%s]\n" % today
        msg = msg + "===================================================="
        for key in transactions.iterkeys():
            
            total = 0
            t_list = transactions[key]
            
            msg += "\n" + "[%s] transactions (with status %s) were found" % (len(t_list), key) + "\n\n"
            for transaction in t_list:
                msg += "\t transaction_id : %s\n" % transaction.id
                msg += "\t type : %s\n" % transaction.type
                msg += "\t amount : u$s %s\n" % transaction.amount
                msg += "\t subscription_id : %s\n" % transaction.subscription_id
                for key in transaction.customer.keys():
                    val = transaction.customer[key]
                    if val:
                        msg += "\t customer_%s : %s\n" % (key, transaction.customer[key])
                total += decimal.Decimal(transaction.amount)
                msg += "\t - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
            msg += "\nTOTAL : u$s %s\n" % total     
            msg += "===============================================================\n"
        send_mail('Daily Transaction Statuses', msg, 'admin@greatcoins.com',  [b for (a,b) in settings.ADMINS], fail_silently=True)
        logging.debug(msg)
    except Exception, e:
        send_mail('Error when trying to get daily transaction statuses', e , 'admin@greatcoins.com', [b for (a,b) in settings.ADMINS], fail_silently=True)
        
        
if __name__ == "__main__":
    send_daily_transactions_notifications()