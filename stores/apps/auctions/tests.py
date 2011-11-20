"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from auctions.models import AuctionSession
from shops.models import Shop
        
class AuctionsTest(TestCase):
    fixtures = [
        'greatcoins_market.json', 
        'greatcoins_subscriptions.json', 
        'greatcoins_auth.json', 
        'greatcoins_shops.json',
        'greatcoins_preferences.json',
        'greatcoins_themes.json'
    ]
    urls = 'stores.urls'
    
    def test_auctions_list(self):
        """
        """
        shop = Shop.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        response = self.client.get(reverse("inventory_auctions"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "failed to access inventory auctions (inventory > auctions)")
        
        response = self.client.get(reverse('auction_add'), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "failed to access auctions add (inventory > add auction)")
        
        
    def test_auction_add_and_details(self):
        shop = Shop.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        date_from = time_from = datetime.datetime.now() 
        date_to = time_to = date_from + datetime.timedelta(days=3)
        
        auction_data = {
                        'date_from': "%s/%s/%s" % (date_from.month, date_from.day, date_from.year), 
                        'time_from': "%s:%s" % (time_from.hour, time_from.minute),
                        'time_to': "%s:%s" % (time_to.hour, time_to.minute),
                        'date_to': "%s/%s/%s" % (date_to.month, date_to.day, date_to.year),
                        'title' : 'Thursday Night Session',
                        'description': 'No description',
        }
        
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 0)
        
        response = self.client.post(reverse('auction_add'), auction_data , HTTP_HOST=HTTP_HOST)
        
        self.assertEqual(response.status_code, 302)
              
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 1)
        
        #should be at least one! the previously added...
        auction = auctions[0]
        response = self.client.get(reverse('auction_details', args=[auction.id]), HTTP_HOST=HTTP_HOST)
        self.assertContains(response, "Thursday Night Session", count=None, status_code=200, msg_prefix='')
        
    
    def test_model_methods(self):
        shop = Shop.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 0)
        
        #Save an active session
        starting_date = datetime.datetime.now() 
        end_date = starting_date + datetime.timedelta(days=3)
        
        auction = AuctionSession(shop=shop, title="Friday Night Session", description="No description for now", start=starting_date, end=end_date)
        auction.save()
        
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 1, "There should be at least one auction session in the db")
        
        auction = auctions[0]
        self.assertEqual(auction.title, "Friday Night Session")
        self.assertEqual(auction.description, "No description for now")
        
        self.assertEqual(auction.finished(), False)
        self.assertEqual(auction.actual(), True)
        self.assertEqual(auction.future(), False)
        
        self.assertEqual(auction.status(), "In Progress")
        self.assertEqual(auction.count_lots(), 0)
        
        #Save a session that will be in the future
        now = datetime.datetime.now()
        starting_date = now + datetime.timedelta(3) 
        end_date = starting_date + datetime.timedelta(days=7)
        
        auction = AuctionSession(shop=shop, title="Next week Session", description="No description for now", start=starting_date, end=end_date)
        auction.save()
        
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 2, "There should be 2 sessions")
        
        auction = auctions[1]
        self.assertEqual(auction.title, "Next week Session")
        self.assertEqual(auction.description, "No description for now")
        
        self.assertEqual(auction.finished(), False)
        self.assertEqual(auction.actual(), False)
        self.assertEqual(auction.future(), True)
        
        self.assertEqual(auction.status(), "Future")
        self.assertEqual(auction.count_lots(), 0)
        
        
        #Save a finished session
        now = datetime.datetime.now()
        starting_date = now - datetime.timedelta(7) 
        end_date = now - datetime.timedelta(days=5)
        
        auction = AuctionSession(shop=shop, title="Finished Session", description="No description for now", start=starting_date, end=end_date)
        auction.save()
        
        auctions = AuctionSession.objects.all()
        self.assertEqual(auctions.count(), 3, "There should be 3 sessions")
        
        auction = auctions[2]
        self.assertEqual(auction.title, "Finished Session")
        self.assertEqual(auction.description, "No description for now")
        
        self.assertEqual(auction.finished(), True)
        self.assertEqual(auction.actual(), False)
        self.assertEqual(auction.future(), False)
        
        self.assertEqual(auction.status(), "Finished")
        self.assertEqual(auction.count_lots(), 0)
        
        print "Done.."
            
        
    def test_for_sale_list(self):
        """
        """
        from shops.models import Shop
        shop = Shop.objects.all()[0]
        HTTP_HOST = shop.default_dns
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        response = self.client.get(reverse("inventory_items"), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "failed to access inventory items (inventory > items for sale > add item)")
        
        response = self.client.get(reverse('item_add'), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "failed to access add new for sale item (inventory > )")
        
        response = self.client.get(reverse('inventory_items_import'), HTTP_HOST=HTTP_HOST)
        self.assertEqual(response.status_code, 200, "failed to access items for sale import (inventory > import items)")

    

        
