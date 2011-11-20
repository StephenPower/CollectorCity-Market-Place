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

import settings
setup_environ(settings)

from sell.models import Sell
from shops.models import Shop
from market_buy.models import BestSeller

def get_week_top_seller():
    
    delta = 7
    date_to = datetime.datetime.now()
    date_from = date_to - datetime.timedelta(delta)
    
    shops = Shop.objects.all()
    max_revenue = -1
    winner = None
    
    logging.info("Calculating the best seller of the week. From: %s - %s" % (date_from, date_to))
    
    for shop in shops:
        
        week_revenue = 0
        sell_week_revenue = Sell.objects.filter(shop=shop)
        sell_week_revenue = sell_week_revenue.filter(date_time__range=(date_from, date_to))
        logging.info(sell_week_revenue)
        for sell in sell_week_revenue:
            week_revenue += sell.total_without_taxes()
          
        logging.info("Total Revenue from shop %s = %s" % (shop, week_revenue))
        
        if week_revenue > max_revenue: 
            winner = shop
            max_revenue = week_revenue
            
    best_seller = BestSeller()
    best_seller.shop = winner
    best_seller.from_date = date_from
    best_seller.to_date = date_to
    best_seller.revenue = max_revenue
    best_seller.save()
    logging.info("Winner: %s" % best_seller)
        
if __name__ == "__main__":
    get_week_top_seller()