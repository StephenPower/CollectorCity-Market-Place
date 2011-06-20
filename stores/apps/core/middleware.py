#from django.http import Http404
#from django.core.exceptions import ObjectDoesNotExist

#from shops.models import Shop
from preferences.models import DnsShop

import re, logging

class SubdomainMiddleware:

    def process_request(self, request):
        url= request.get_host()
        match = re.search(r"^(http://)?(?P<dns>.*.com)", url)
        if match:
            dns = match.group('dns')
            try:
                shop = DnsShop.objects.filter(dns=dns).get().shop
                if shop.is_active(): request.shop = shop
                else: request.shop = None
            except:
                request.shop = None
        else:
            request.shop = None
#        domain_parts = request.get_host().split('.')
#        if (len(domain_parts) > 2):
#            subdomain = domain_parts[0]
#            if (subdomain.lower() == 'www'):
#                subdomain = None
#            domain = '.'.join(domain_parts[1:])
#        else:
#            subdomain = None
#            domain = request.get_host()
#        
#        request.subdomain = subdomain
#        request.domain = domain
#
#        if subdomain:
#            
#            if subdomain != 'www' and subdomain != '':
#                # find shop
#                try:
#                    request.shop = Shop.objects.filter(name=subdomain).get()
#                except ObjectDoesNotExist:
#                    raise Http404
#        else:
#            request.shop = None
    
