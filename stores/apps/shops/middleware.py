#from django.http import Http404
#from django.core.exceptions import ObjectDoesNotExist

#from shops.models import Shop
from sell.models import Cart
 
import logging

class CartMiddleware:

    def process_request(self, request):
        user= request.user
        shop = request.shop        
        
        if (shop is not None) and (user is not None) and (user.is_anonymous() == False) and (user != shop.admin):
            try:
                cart = Cart.objects.filter(bidder=user).filter(shop=shop).get()
            except Cart.DoesNotExist:
                cart = Cart(shop=shop, bidder=user)
                cart.save()
            request.cart = cart