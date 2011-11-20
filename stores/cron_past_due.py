#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ
from django.core.mail import send_mail
#from django.db import transaction

import settings
setup_environ(settings)

from payments.gateways.braintreegw import BraintreeGateway
from subscriptions.models import Subscription

def send_past_due_notification():
    gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
    past_due_days = 2
    subscriptions = gw.get_past_due_subscriptions(past_due_days)
    logging.info("%s subscriptions were found with status past due" % len(subscriptions))
    for subscription in subscriptions:
        try:
            local_subscription = Subscription.objects.filter(subscription_id=subscription.id).get()
            #Send email to Site Admin    
            msg = "We have found that Subscription (id=%s, plan=%s) for shop %s is past due. An email to shop owner will be sent to inform about this situation" % (local_subscription.subscription_id, local_subscription.plan.name ,local_subscription.owner.shop) 
            logging.info(msg)
            send_mail('Past due Subscription', msg, settings.EMAIL_FROM, [b for (a,b) in settings.STAFF], fail_silently=True)
            #Send email to shop owner
            msg = "We notice you that your subscription (%s) for shop %s is %s days past due." % (local_subscription.plan.name ,local_subscription.owner.shop, past_due_days) 
            send_mail('Past due Suscription', msg, settings.EMAIL_FROM,  [local_subscription.owner.user.email], fail_silently=True)
        except Subscription.DoesNotExist:
            error_msg = "Subscription<id%s> was not found. A past due subscription was found in braintree, but this subscription do not correspond with any in the system" % subscription.id
            logging.error(error_msg)
            send_mail('Subscription not found', error_msg , settings.EMAIL_FROM, [b for (a,b) in settings.STAFF], fail_silently=True)
        
        except Exception, e:
            send_mail('Error when trying to check past due subscriptions', e , settings.EMAIL_FROM, [b for (a,b) in settings.STAFF], fail_silently=True)
        
        
if __name__ == "__main__":
    send_past_due_notification()