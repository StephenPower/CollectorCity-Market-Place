"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime
import decimal
import logging
import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from market.models import MarketCategory
from shops.models import Shop
from sell.models import Cart
from auctions.models import AuctionSession
from lots.models import Lot, BidderIncrementCalculator
from for_sale.models import Item


class StoreAdminTest(TestCase):
    fixtures = [
        'greatcoins_market.json', 
        'greatcoins_subscriptions.json', 
        'greatcoins_auth.json', 
        'greatcoins_shops.json',
        'greatcoins_preferences.json',
        'greatcoins_themes.json'
    ]
    
    def test_urls_access(self):
        
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        shop = Shop.objects.all()[0]
        category = MarketCategory.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        auction = AuctionSession(shop=shop, title="Auction Session Nr 0", description="-- no desc --", start=now, end=tomorrow)
        auction.save()
        
        lot = Lot(shop = shop,
                  title = "Coin From Egypt 1905 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  session=auction, 
                  starting_bid=decimal.Decimal("10.00"), 
                  reserve=decimal.Decimal("0.00"))
        lot.save()
        
        item = Item(shop = shop,
                  title = "Coin From Rusia 1917 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  qty = "10",
                  price = decimal.Decimal("150"))
        item.save()
        
        user = shop.admin
#        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to view lot")
#       
        success = self.client.login(username=user.username, password="test")
        self.assertEqual(success, True, "Login failed")
         
        ############# CUSTOMERS ################
        response = self.client.get(reverse("home_admin"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach home_admin")
        
        response = self.client.get(reverse("customers"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers")
        
        response = self.client.get(reverse("customers_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_overview")
        
        response = self.client.get(reverse("customers_profiles"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_profiles")
        
        response = self.client.get(reverse("customers_sold_items"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_sold_items")
        
        response = self.client.get(reverse("customers_payments"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_payments")
        
        response = self.client.get(reverse("customers_shipments"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_shipments")
        
        response = self.client.get(reverse("customers_wish_lists"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_wish_list")
        
#        response = self.client.get(reverse("customers_send_notification"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to bid a valid amount")
        
        response = self.client.get(reverse("customers_mailing_list"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_mailing_list")
        
        response = self.client.get(reverse("customers_export_mailinglist"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach customers_export_mailinglist")
        
        ######### WEBSTORE ############
        response = self.client.get(reverse("web_store"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store")
        
        response = self.client.get(reverse("web_store_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_overview")
        
        response = self.client.get(reverse("web_store_marketing"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_marketing")
        
        response = self.client.get(reverse("web_store_shows"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_shows")
        
#        response = self.client.get(reverse("web_store_theme"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_theme")
        
        response = self.client.get(reverse("web_store_pages"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_pages")
        
        response = self.client.get(reverse("web_store_blogs"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_blogs")
        
        response = self.client.get(reverse("web_store_navigation"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach web_store_navigation")
        
#        response = self.client.get(reverse("web_store_show_go"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to bid a valid amount")
#        
#        response = self.client.get(reverse("web_store_show_not_go"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to bid a valid amount")
#        
#        response = self.client.get(reverse("web_store_theme"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 200, "Failed when trying to bid a valid amount")
        
        ######### INVENTORY ##########
        response = self.client.get(reverse("inventory"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory")
        
        response = self.client.get(reverse("inventory_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_overview")
        
        response = self.client.get(reverse("inventory_items"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_items")
        
        response = self.client.get(reverse("inventory_items_import"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_items_import")
        
        response = self.client.get(reverse("inventory_lots"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_lots")
                
        response = self.client.get(reverse("inventory_auctions"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_auctions")
        
        response = self.client.get(reverse("inventory_categorize"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach inventory_categorize")
        
        ######## ACCOUNT #########
        response = self.client.get(reverse("account"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach account")
        
        response = self.client.get(reverse("account_profile"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach account_profile")
        
        response = self.client.get(reverse("account_password"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach account_password")
        
        response = self.client.get(reverse("add_profile_photo"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach add_profile_photo")
        
        response = self.client.get(reverse("preferences"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to reach preferences")
    
    
    def test_urls_access_denied(self):
        
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        shop = Shop.objects.all()[0]
        category = MarketCategory.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        auction = AuctionSession(shop=shop, title="Auction Session Nr 0", description="-- no desc --", start=now, end=tomorrow)
        auction.save()
        
        lot = Lot(shop = shop,
                  title = "Coin From Egypt 1905 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  session=auction, 
                  starting_bid=decimal.Decimal("10.00"), 
                  reserve=decimal.Decimal("0.00"))
        lot.save()
        
        item = Item(shop = shop,
                  title = "Coin From Rusia 1917 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  qty = "10",
                  price = decimal.Decimal("150"))
        item.save()
        
        ############# CUSTOMERS ################
        response = self.client.get(reverse("home_admin"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach home_admin")
        
        response = self.client.get(reverse("customers"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers")
        
        response = self.client.get(reverse("customers_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_overview")
        
        response = self.client.get(reverse("customers_profiles"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_profiles")
        
        response = self.client.get(reverse("customers_sold_items"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_sold_items")
        
        response = self.client.get(reverse("customers_payments"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_payments")
        
        response = self.client.get(reverse("customers_shipments"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_shipments")
        
        response = self.client.get(reverse("customers_wish_lists"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_wish_list")
        
#        response = self.client.get(reverse("customers_send_notification"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount")
        
        response = self.client.get(reverse("customers_mailing_list"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_mailing_list")
        
        response = self.client.get(reverse("customers_export_mailinglist"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach customers_export_mailinglist")
        
        ######### WEBSTORE ############
        response = self.client.get(reverse("web_store"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store")
        
        response = self.client.get(reverse("web_store_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_overview")
        
        response = self.client.get(reverse("web_store_marketing"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_marketing")
        
        response = self.client.get(reverse("web_store_shows"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_shows")
        
#        response = self.client.get(reverse("web_store_theme"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_theme")
        
        response = self.client.get(reverse("web_store_pages"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_pages")
        
        response = self.client.get(reverse("web_store_blogs"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_blogs")
        
        response = self.client.get(reverse("web_store_navigation"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach web_store_navigation")

#        self.assertRedirects(response, "/login/", status_code=302, target_status_code=200, msg_prefix='')
#        response = self.client.get(reverse("web_store_show_go"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount")
#        
#        response = self.client.get(reverse("web_store_show_not_go"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount")
#        
#        response = self.client.get(reverse("web_store_theme"), HTTP_HOST=HTTP_HOST)
#        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount")
        
        ######### INVENTORY ##########
        response = self.client.get(reverse("inventory"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory")
        
        response = self.client.get(reverse("inventory_overview"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_overview")
        
        response = self.client.get(reverse("inventory_items"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_items")
        
        response = self.client.get(reverse("inventory_items_import"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_items_import")
        
        response = self.client.get(reverse("inventory_lots"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_lots")
                
        response = self.client.get(reverse("inventory_auctions"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_auctions")
        
        response = self.client.get(reverse("inventory_categorize"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach inventory_categorize")
        
        ######## ACCOUNT #########
        response = self.client.get(reverse("account"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach account")
        
        response = self.client.get(reverse("account_profile"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach account_profile")
        
        response = self.client.get(reverse("account_password"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach account_password")
        
        response = self.client.get(reverse("add_profile_photo"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach add_profile_photo")
        
        response = self.client.get(reverse("preferences"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to reach preferences")