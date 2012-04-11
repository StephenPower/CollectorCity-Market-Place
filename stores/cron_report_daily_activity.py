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

"""
Daily Activity (Sign Up / Cancel)
Total Customers    
Total Sign Ups This Month    
Total Sign Ups This Today    
Total Cancelations This Month    
Total Cancelations This Today
"""

def report_daily_activity():
    from django.core.mail import EmailMultiAlternatives
    from django.template import Context, loader
    from reports.views import get_daily_activity_data
    
    day = datetime.datetime.now()
    
    try:
        t_txt = loader.get_template("admin/mail/daily_activity_report.txt")
        t_html = loader.get_template("admin/mail/daily_activity_report.html")        
        
        c = get_daily_activity_data(day)
         
        subject, from_email, to = 'Daily Activity Report', "no-reply@greatcoins.com", "admin@greatcoins.com"
        text_content = t_txt.render(Context(c))
        html_content = t_html.render(Context(c))
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
                
    except Exception, e:
        logging.info(e)
        mail = EmailMessage(subject='Error when trying to generate Daily Activity Report',
                            body=e,
                            from_email=settings.EMAIL_FROM,
                            to=[mail for (name, mail) in settings.STAFF],
                            headers={'X-SMTPAPI': '{\"category\": \"Error\"}'})
        mail.send(fail_silently=True)
#        send_mail('Error when trying to generate Daily Activity Report', e , settings.EMAIL_FROM, [mail for (name, mail) in settings.STAFF], fail_silently=True)
#        send_mail('Error when trying to generate Daily Activity Report', e , settings.EMAIL_FROM, ["martinriva@gmail.com"], fail_silently=True)
        
        
if __name__ == "__main__":
    report_daily_activity()