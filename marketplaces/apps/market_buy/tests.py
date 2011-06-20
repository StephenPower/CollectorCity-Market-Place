"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import logging

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from auth.models import User

class MarketSellTest(TestCase):
    fixtures = [
        'greatcoins_market.json', 
        'greatcoins_subscriptions.json', 
        'greatcoins_auth.json', 
        'greatcoins_shops.json',
        'greatcoins_preferences.json',
        'greatcoins_themes.json'
    ]
    
    def setUp(self):
        
        try:
            user = User.objects.get(username="test")
            user.delete()
        except User.DoesNotExist:
            pass
        
    def test_sign_up(self):
        """
        """
        if settings.SITE_RUNNING_MODE  != 'marketplaces':
            return
        
        from shops.models import Shop
        shop = Shop.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        
        response = self.client.get(reverse("market_buy_signup"), HTTP_HOST=HTTP_HOST)
        
        self.failUnless(response.status_code, 200)
        
        users_count = User.objects.count()
        params = {
            'username': 'test',
            'email': 't@t.com',
            'password1': 'test',
            'password2': 'test',
        }
        
        response = self.client.post(reverse("market_buy_signup"), params)
        self.failUnless(response.status_code, 302)
        
        self.assertEquals(User.objects.count(), users_count + 1)
        
        
        

