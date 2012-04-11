#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from django.core.urlresolvers import reverse
from blog_pages.models import Post

"""
This cron sends an email to those users that have post in drafts.
It should run once a day. At the midnight
"""
def send_posts_ind_draft_reminder():
    
    date = datetime.datetime.now() - datetime.timedelta(hours=24)
    posts = Post.objects.filter(draft=True, date_time__lt=date).order_by("shop")
    already_notified = set()
        
    try:
        for post in posts:
            shop = post.shop
            if shop not in already_notified:
                link = "http://%s%s" % (shop.default_dns, reverse("post_edit", args=[post.id]))
                msg = "\n\nWe remember you that you have posts in a draft status on your %s shop. If you want that posts appears on you site you must publish them.\n\nGo to %s and make it public!" % (shop, link)
                mail = EmailMessage(subject='Posts in draft reminder',
                                    body=msg,
                                    from_email=settings.EMAIL_FROM,
                                    to=[shop.owner().email],
                                    headers={'X-SMTPAPI': '{\"category\": \"Posts In Draft Reminder\"}'})
                mail.send(fail_silently=True)   
#                send_mail('Posts in draft reminder', msg, settings.EMAIL_FROM, [shop.owner().email], fail_silently=True)
                already_notified.add(shop)
    except Exception, e:
        mail = EmailMessage(subject='Error when trying to send email notifying that customer have "posts in draft"',
                            body=e,
                            from_email=settings.EMAIL_FROM,
                            to=[mail for (name, mail) in settings.STAFF],
                            headers={'X-SMTPAPI': '{"category": "Error"}'})
        mail.send(fail_silently=True)
#        send_mail('Error when trying to send email notifying that customer have "posts in draft"', e , settings.EMAIL_FROM, [mail for (name, mail) in settings.STAFF], fail_silently=True)


if __name__ == "__main__":
    send_posts_ind_draft_reminder()