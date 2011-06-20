"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime
import decimal
import cron
import logging
import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from auctions.models import AuctionSession
from blog_pages.models import Home, About, Post, Page
from for_sale.models import Item
from lots.models import Lot, BidderIncrementCalculator
from market.models import MarketCategory, MarketSubCategory
from shops.models import Shop
from sell.models import Cart




class BiddingTest(TestCase):
    fixtures = [
        'greatcoins_market.json', 
        'greatcoins_subscriptions.json', 
        'greatcoins_auth.json', 
        'greatcoins_shops.json',
        'greatcoins_preferences.json',
        'greatcoins_themes.json'
    ]
    
    
    def setUp(self):
        
        shop = Shop.objects.all()[0]
        about = About(shop=shop)
        about.save()
        
        home = Home(shop=shop)
        home.save()
        
        self.shop = shop
        self.HTTP_HOST = self.shop.default_dns     
        
    def test_bidding_place_bid(self):
        """
        """
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        
        category = MarketCategory.objects.all()[0]
        
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        
        # Creates an auction
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 0", description="-- no desc --", start=now, end=tomorrow)
        auction.save()
        
        # Creates a lot 
        lot = Lot(shop = self.shop,
                  title = "Coin From Egypt 1905 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  session=auction, 
                  starting_bid=decimal.Decimal("10.00"), 
                  reserve=decimal.Decimal("0.00"))
        lot.save()
        
        # Ttry to login
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed when trying to view lot")
        
        # Check than when is created there is no any bid
        lot = Lot.objects.get(id=lot.id)
        self.assertEqual(lot.bid_actual, None)
        
        # Testing bid increment table
        increment_calculator = BidderIncrementCalculator()
        #from    0.01    to    0.99   --> 0.05
        #from    1.00    to    4.99   --> 0.25
        #from    5.00    to    24.99   --> 0.50
        #from    25.00   to    99.99   --> 1.00
        #from    100.00  to    249.99  --> 2.50
        #from    250.00  to    499.99  --> 5.00
        #from    500.00  to    999.99  --> 10.00
        #from    1000.00 to    2499.99 --> 25.00
        #from    2500.00 to    4999.99 --> 50.00
        #from    5000.00 to    99999.99--> 100.00
        
        for i in range(30):
            lot = Lot.objects.get(id=lot.id)
            if lot.bid_actual:
                logging.info("Current Bid: %s" % (lot.bid_actual.bid_amount))
                
            else:
                logging.info("Starting Bid: %s" % (lot.starting_bid))
                
            min_bid = lot.next_bid_from()
            (from_price, to_price, inc) = increment_calculator.match_for(min_bid)
            logging.info("From: %s To: %s Bid must be grater than %s (increment to be applied %s)" % (from_price, to_price, min_bid, inc))
            
            logging.info("Minimum Bid allowed: %s" % min_bid)
            
            # Should not be allowed to bid
            wrong_bid = min_bid - (min_bid * decimal.Decimal(("0.1")))
            logging.info("Testing Invalid Bidding Price: %s" % wrong_bid)
            response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': wrong_bid}, HTTP_HOST=self.HTTP_HOST)
            self.assertEqual(response.status_code, 200, "Failed: This bid shouldn't be valid!!")
            
            # Should be allowed to bid
            string_format = '%.2f' % (min_bid + (min_bid * decimal.Decimal(("0.5"))))
            valid_bid = decimal.Decimal((string_format))
            logging.info("Testing Valid Bidding Price: %s" % valid_bid)       
            response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': valid_bid}, HTTP_HOST=self.HTTP_HOST)
            self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount %s. This value should be allowed..." % valid_bid)
            
            # Check that last bid is the the currently lot.bid_actual
            logging.info("Testing Correct Lot.bid_actual: %s" % valid_bid) 
            lot = Lot.objects.get(id=lot.id)
            self.assertEqual(lot.bid_actual.bid_amount, valid_bid, "Failed: The bid actual is wrong, is %s but should be %s" % (lot.bid_actual.bid_amount, valid_bid))
            
    def test_lot_sold(self):
        """
        """       
        
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        category = MarketCategory.objects.all()[0]
        
        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(seconds=5)
        
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 1", description="-- no desc --", start=now, end=now_plus_10)
        auction.save()
        
        lot = Lot(shop = self.shop,
                  title = "Coin From Rusia 1901 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  session=auction, 
                  starting_bid=decimal.Decimal("10.00"), 
                  reserve=decimal.Decimal("0.00"))
        lot.save()
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        bidder = User.objects.filter(username="test").get()
        cart = Cart(shop=self.shop, bidder=bidder)
        cart.save()
        
        #Check that lot is still active...
        self.assertEqual(lot.is_active(), True , "Failed: The lot should be active!")
        self.assertEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should not have any bid yet!")
        
        my_bid = decimal.Decimal("19.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount $19.00. This value should be allowed...")    
        
        lot = Lot.objects.get(id=lot.id)
        
        self.assertNotEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should have at least one bid!")
        logging.info("waiting to auction session finish...")
        
        while not lot.session.finished():
            time.sleep(1)
            
        logging.info("Running cron...")
        cron.minute_update()
        
        lot = Lot.objects.get(id=lot.id)

        self.assertEqual(lot.reserve_has_been_met(), True , "Failed, reserved has not been met!")
        self.assertEqual(lot.bid_actual.bid_amount, my_bid , "Failed: The bid actual is wrong, is %s but should be %s" % (lot.bid_actual.bid_amount, my_bid))
        self.assertEqual(lot.bid_actual.bidder.username, "test" , "Failed, wrong bidder won!")
        self.assertEqual(lot.is_active(), False, "Failed: The lot state is wrong, should be SOLD but it is %s" % lot.state)
        self.assertEqual(lot.is_didnt_sell(), False, "Failed: The lot state is wrong, should be SOLD but it is %s" % lot.state)
        self.assertEqual(lot.is_sold(), True, "Failed: The lot state is wrong, should be SOLD but it is %s" % lot.state)

    def test_lot_didnt_sell(self):
        """
        Check that a lot get state DIDN'T SELL when there no bidding...
        """       
        
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        category = MarketCategory.objects.all()[0]
        
        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(seconds=5)
        
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 2", description="-- no desc --", start=now, end=now_plus_10)
        auction.save()
        
        lot = Lot(shop = self.shop,
                  title = "Coin From Argentina 1890 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight = "5",
                  session=auction, 
                  starting_bid=decimal.Decimal("100.00"), 
                  reserve=decimal.Decimal("0.00"))
        lot.save()
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        #Check that lot is still active...
        self.assertEqual(lot.is_active(), True , "Failed: The lot should be active!")
        self.assertEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should not have any bid yet!")
        
        my_bid = decimal.Decimal("90.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed: this bid is not valid...")    
        
        self.assertEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should not have any bid yet!")
        
        logging.info("waiting to auction session finish...")
        
        while not lot.session.finished():
            time.sleep(1)
        
        logging.info("Running cron...")
        cron.minute_update()
        
        lot = Lot.objects.get(id=lot.id)

        self.assertEqual(lot.reserve_has_been_met(), False , "Failed, the reserved price should not be reached!")
        self.assertEqual(lot.bid_actual, None , "Failed: There were no bids! ")
        self.assertEqual(lot.is_active(), False, "Failed: The lot could not be active, the lot finished and there were no bids!")
        self.assertEqual(lot.is_sold(), False, "Failed: The lot could not be sold, there were no bids!")
        self.assertEqual(lot.is_didnt_sell(), True, "Failed: The lot wasn't sell!")
    
    def test_lot_didnt_sell2(self):
        """
        Check that a lot get state DIDN'T SELL when there are no biddings that reach the reserve price
        """       
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
        
        category = MarketCategory.objects.all()[0]
        
        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(seconds=5)
        
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 3", description="-- no desc --", start=now, end=now_plus_10)
        auction.save()
        
        lot = Lot(shop=self.shop,
                  title = "Coin From Brasil 1900 (PCGS 60)",
                  description = "rare coin",
                  category = category,
                  date_time = now,
                  weight="5",
                  session=auction, 
                  starting_bid=decimal.Decimal("100.00"), 
                  reserve=decimal.Decimal("300.00"))
        lot.save()
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        #Check that lot is still active...
        self.assertEqual(lot.is_active(), True , "Failed: The lot should be active!")
        self.assertEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should not have any bid yet!")
        
        #1) Trying To BID wrong
        my_bid = decimal.Decimal("90.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200, "Failed: this bid is not valid...")    
        self.assertEqual(lot.bidhistory_set.all().count(), 0 , "Failed: The lot should not have any bid yet!")
        
        #2) First valid bid, but don't reach the reserve price
        my_bid = decimal.Decimal("120.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount %s. This value should be allowed..." % my_bid)    
        
        lot = Lot.objects.get(id=lot.id)
        self.assertEqual(lot.bidhistory_set.all().count(), 1 , "Failed: The lot should have 1 bid!")
        
        #3) Second valid bid, but neither reach the reserve price
        my_bid = decimal.Decimal("290.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount %s. This value should be allowed..." % my_bid)    
        
        lot = Lot.objects.get(id=lot.id)
        self.assertEqual(lot.bidhistory_set.all().count(), 2 , "Failed: The lot should have 2 bids!")
        
        logging.info("waiting to auction session finish...")
        while not lot.session.finished():
            time.sleep(1)
            
        logging.info("Running cron...")
        cron.minute_update()
        
        lot = Lot.objects.get(id=lot.id)

        self.assertEqual(lot.reserve_has_been_met(), False , "Failed, the reserved price should not be reached!")
        self.assertEqual(lot.bid_actual.bid_amount, my_bid, "Failed: The bid actual is wrong, is %s but should be %s" % (lot.bid_actual.bid_amount, my_bid))
        self.assertEqual(lot.bid_actual.bidder.username, "test" , "Failed, wrong bidder won!")
        self.assertEqual(lot.is_sold(), False, "Failed: The lot state is wrong, should be DIDN'T SELL but it is %s" % lot.state)
        self.assertEqual(lot.is_didnt_sell(), True, "Failed: The lot state is wrong, should be DIDN'T SELL but it is %s" % lot.state)
        
    def test_lot_still_active(self):
        """
        Check that nothing happend to those lots that aren't finished yet when cron is executed
        """ 
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
    
        category = MarketCategory.objects.all()[0]
        
        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(seconds=5)
        
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 4", description="-- no desc --", start=now, end=now_plus_10)
        auction.save()
        
        lot = Lot(shop=self.shop,
                  title="Coin From USA 1905 (PCGS 50)",
                  description="rare coin",
                  category=category,
                  date_time=now,
                  weight="5",
                  session=auction, 
                  starting_bid=decimal.Decimal("100.00"), 
                  reserve=decimal.Decimal("300.00"))
        lot.save()
        
        success = self.client.login(username='test', password='test')
        self.assertEqual(success, True, "login failed")
        
        my_bid = decimal.Decimal("120.00")
        response = self.client.get(reverse("bidding_view_lot", args=[lot.id]), {'amount': my_bid}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302, "Failed when trying to bid a valid amount %s. This value should be allowed..." % my_bid)    
        
        lot = Lot.objects.get(id=lot.id)
        self.assertEqual(lot.bidhistory_set.all().count(), 1 , "Failed: The lot should not have any bid yet!")
        
        logging.info("don't wait for auction session to finish...")

        #Check that lot is still active...
        lot = Lot.objects.get(id=lot.id)
        self.assertEqual(lot.is_active(), True , "Failed: The lot should be active!")

        logging.info("Running cron...")
        
        cron.minute_update()
        
        lot = Lot.objects.get(id=lot.id)

        self.assertEqual(lot.is_active(), True , "Failed: The lot should be active!")
        self.assertEqual(lot.bid_actual.bid_amount, my_bid, "Failed: The bid actual is wrong, is %s but should be %s" % (lot.bid_actual.bid_amount, my_bid))
        self.assertEqual(lot.bid_actual.bidder.username, "test" , "Failed, wrong bidder won!")
        self.assertEqual(lot.is_sold(), False, "Failed: The lot state is wrong, should be ACTIVE but it is %s" % lot.state)
    
    def test_bidding_home(self):
        
        category = MarketCategory.objects.all()[0]
        subcategory = MarketSubCategory.objects.all()[0]

        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(seconds=5)
        
        auction = AuctionSession(shop=self.shop, title="Auction Session Nr 4", 
                                 description="-- no desc --", 
                                 start=now, 
                                 end=now_plus_10)
        auction.save()
        
        lot = Lot(shop=self.shop,
                  title="Coin From USA 1905 (PCGS 50)",
                  description="rare coin",
                  category=category,
                  date_time=now,
                  weight="5",
                  session=auction, 
                  starting_bid=decimal.Decimal("100.00"), 
                  reserve=decimal.Decimal("300.00"))
        lot.save()
        
        item = Item(shop=self.shop, title="Item", description="an item", 
                    price="10.0", 
                    category=category, 
                    subcategory=subcategory, 
                    qty=2, weight="2.0")
        item.save() 
        
        response = self.client.post(reverse("bidding_home"), {'email': "some@email.com"}, HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302)
            
#            param = {
#             'about': about,
#             'home': 
#                {
#                 'title': home.title, 
#                 'body': home.body, 
#                 'image': home.image
#                 },
#             'last_post': last_post,
#             'mailing_list': block_mailing_list,
#             'new_items': new_items,
#             'page_title': 'Home',
#             'page_description': striptags(home.body),
#             'sessions': new_sessions,
#            }
            
        response = self.client.get(reverse("bidding_home"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        
        #i don't know why context don't have this values, check it later
#        self.assertEqual(len(response.context['new_items']), 1)
#        self.assertEqual(len(response.context['sessions']), 1)
#        self.assertEqual(len(response.context['last_post']), 1)
#        self.assertEqual(response.context['page_title'], "Home")
#        self.assertEqual(response.context['home']['title'], "Welcome to My Store")
#        self.assertEqual(response.context['home']['body'], "Praesent a enim ac nunc egestas egestas. Integer auctor justo et lorem pulvinar eleifend. Curabitur accumsan massa lectus. Pellentesque ac ipsum sed odio mattis aliquam at egestas odio. Vestibulum gravida augue sapien, sit amet posuere quam. Duis dui mauris, pretium sed cursus quis, semper vitae metus. Sed et ante quam. Morbi nunc diam, tristique at vulputate a, ornare sed odio. Donec semper dolor nisl. Maecenas ac felis mauris, eget ornare metus. Pellentesque ac vehicula ligula. Nam semper nibh quis tortor eleifend et ultricies sapien tempus.")

        
    def test_bidding_views(self):
        
        now = datetime.datetime.now()
        tomarrow = now + datetime.timedelta(days=1)
        category = MarketCategory.objects.all()[0]
        subcategory = MarketSubCategory.objects.all()[0]
        
        item = Item(shop=self.shop, title="My Unique Item", description="the description of my unique item", 
                    price="10.0", 
                    category=category, 
                    subcategory=subcategory, 
                    qty=2, weight="2.0")
        item.save() 
        
        auction = AuctionSession(shop=self.shop, title="Test Session", 
                                 description="-- no desc --", 
                                 start=now, 
                                 end=tomarrow)
        auction.save()
        
        lot = Lot(shop=self.shop,
                  title="Coin From USA 1905 (PCGS 50)",
                  description="rare coin",
                  category=category,
                  date_time=now,
                  weight="5",
                  session=auction, 
                  starting_bid=decimal.Decimal("100.00"), 
                  reserve=decimal.Decimal("300.00"))
        lot.save()
        
        
        response = self.client.get(reverse("bidding_about_us"), HTTP_HOST=self.HTTP_HOST)
        self.assertContains(response, "Nam est mauris, pretium eu imperdiet ut, iaculis sit amet sapien", count=None, status_code=200, msg_prefix='')     
        
        response = self.client.get(reverse("bidding_auctions_id", args=[auction.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sessions']), 1)
        
        response = self.client.get(reverse("bidding_blog"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse("bidding_buy_now", args=[item.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 302)
        
        #bidding_search
    
        page = Page(shop=self.shop, name_link="somewhere", title="Page Title", body="This is the page content")
        page.save()
        response = self.client.get(reverse("bidding_page", args=[page.name_link]), HTTP_HOST=self.HTTP_HOST)
        self.assertContains(response, "Page Title", count=None, status_code=200, msg_prefix='')
        self.assertContains(response, "This is the page content", count=None, status_code=200, msg_prefix='')
        
        response = self.client.get(reverse("bidding_sitemap"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        #self.assertContains(response, "Page Title", count=None, status_code=200, msg_prefix='')
        
        response = self.client.get(reverse("bidding_for_sale"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse("bidding_map", args=[self.shop.about.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
            
        response = self.client.get(reverse("bidding_view_history_lot", args=[lot.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse("bidding_view_history_lot", args=[lot.id]), {'amount': '10.00' },HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse("bidding_view_item", args=[item.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertContains(response, "My Unique Item", count=None, status_code=200, msg_prefix='')
        
        post = Post(shop=self.shop, title="This is my first blog post", body="some content here")
        post.save()
        
        self.assertEqual(post.views, 0)
        response = self.client.get(reverse("bidding_view_post", args=[post.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertContains(response, "This is my first blog post" , count=None, status_code=200, msg_prefix='')
    
        post = Post.objects.filter(id=post.id)[0]
        self.assertEqual(post.views, 1)
    
        
        
        
        
    