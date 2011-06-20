#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import setup_environ

#from django.db import transaction

import datetime
import logging

def minute_update():
    try:
        from auctions.models import AuctionSession
        sessions = AuctionSession.objects.filter(end__lte=datetime.datetime.now())
        for session in sessions:
            logging.info("Session Finished: %s" % session)
            lots = session.lot_set.all()
            for lot in lots:
                logging.info("\t> Lot: %s, state=%s" %(lot, lot.state))
                if lot.state == 'A':
                    if len(lot.bidhistory_set.all()) > 0 and lot.reserve_has_been_met():
                        lot.sold()
                        logging.info("\t\tLot marked as sold")
                    else:
                        lot.didnt_sell()
                        logging.info("\t\tLot marked as didn't sell")
                    lot.save()
    
        logging.info(datetime.datetime.now())
    except Exception, e:
        logging.info(e)
#    transaction.commit_unless_managed()

if __name__ == "__main__":
    import settings
    setup_environ(settings)
    
    minute_update()