import logging
from market.models import MarketPlace
import re

MARKETS = {} 
for market in MarketPlace.objects.all():
    MARKETS[market.base_domain] = market

class MarketPlaceMiddleware:

    def process_request(self, request):
        host = request.get_host()
        request.marketplace = None
        for base_domain, market in MARKETS.iteritems():
            if host.endswith(base_domain):
                request.marketplace = market
                break
            
        if request.marketplace is None:
            request.marketplace = MARKETS.values()[0]
