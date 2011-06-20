"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import logging

from django.test import TestCase
from django.core.urlresolvers import reverse

from auth.models import User
from market.models import MarketPlace


class MarketCommunityTest(TestCase):
    fixtures = [
            'greatcoins_market.json', 
            'greatcoins_subscriptions.json', 
            'greatcoins_auth.json', 
            'greatcoins_shops.json',
            'greatcoins_preferences.json',
            'greatcoins_themes.json'
        ]
    
    def setUp(self):
        from shops.models import Shop
        shop = Shop.objects.all()[0]
        self.HTTP_HOST = shop.default_dns
        
    def test_urls(self):
        """
            Test market community page availability
        """
        response = self.client.get(reverse("market_community") , HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(reverse("community_overview"), HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(reverse("community_blogs"), HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(reverse("community_forums"), HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(reverse("community_faq"), HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(reverse("community_profiles"), HTTP_HOST=self.HTTP_HOST)
        self.failUnless(response.status_code, 200)