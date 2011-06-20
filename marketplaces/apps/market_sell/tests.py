"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import logging

from django.test import TestCase
from django.core.urlresolvers import reverse

from auth.models import User
from shops.models import Shop

class MarketSellTest(TestCase):
    fixtures = ['greatcoins_market.json', 'greatcoins_subscriptions.json']
    
    def setUp(self):
        try:
            user = User.objects.get(username="test_shop_signup")
            user.delete()
        except User.DoesNotExist:
            pass

    def test_sign_up(self):
        """
            Test shop signup
        """

        response = self.client.get(reverse("market_buy_signup"))
        
        self.failUnless(response.status_code, 200)
        
        users_count = User.objects.count()
        params = {
            'username': 'test_shop_signup',
            'email': 'test_shop_signup@t.com',
            'password1': 'test',
            'password2': 'test',
        }
        
        response = self.client.post(reverse("market_buy_signup"), params)
        self.failUnless(response.status_code, 302)
        
        self.assertEquals(User.objects.count(), users_count + 1)
        
        shops_count = Shop.objects.count()
        
        response = self.client.get(reverse("market_sell_signup"))
        self.failUnless(response.status_code, 200)
         
        print response.context
        #SignUp step 0       
        params = {
            'csrfmiddlewaretoken': str(response.context['csrf_token']),
            '0-name_store': 'test2',
            '0-shop_name': 'test2',
            '0-street': 'test',
            '0-city': 'test',
            '0-state': 'NY',
            '0-zip': '10001',
            'wizard_step': '0'
        }

        response = self.client.post(reverse("market_sell_signup"), params)
        self.failUnless(response.status_code, 200)
        
        params = {
            'csrfmiddlewaretoken': str(response.context['csrf_token']),
            '0-name_store': 'test2',
            '0-shop_name': 'test2',
            '0-street': 'test',
            '0-city': 'test',
            '0-state': 'NY',
            '0-zip': '10001',
            '1-plan_id': '1',
            'wizard_step': '1',
            'hash_0':'22267e8560569a5bba749a8f54aab54a',
        }

        response = self.client.post(reverse("market_sell_signup"), params)
        self.failUnless(response.status_code, 200)
        

        params = {
            'csrfmiddlewaretoken': str(response.context['csrf_token']),
            '0-name_store': 'test2',
            '0-shop_name': 'test2',
            '0-street': 'test',
            '0-city': 'test',
            '0-state': 'NY',
            '0-zip': '10001',
            '1-plan_id': '1',
            '2-billing_street': 'el billing street',
            '2-billing_city': 'el billing city',
            '2-billing_state': 'NY',
            '2-billing_zip': '10001',
            '2-cc_number': '4111111111111111',
            '2-cc_expiration_month': '03',
            '2-cc_expiration_year': '2012',
            '2-card_security_number': '123',
            '2-terms': 'on',
            'wizard_step': '2',
            'hash_0':'22267e8560569a5bba749a8f54aab54a',
            'hash_1':'e0341a56bf5d7baa6d13e9b72e831098'
        }

        response = self.client.post(reverse("market_sell_signup"), params)
        self.failUnless(response.status_code, 200)
        
        self.assertEquals(Shop.objects.count(), shops_count + 1)

