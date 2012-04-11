import datetime
import unittest

from auth.models import User
from market.models import MarketPlace, MarketCategory, MarketSubCategory 
from for_sale.models import Item
from sell.models import Cart, ShippingData
from shops.models import Shop

from preferences.models import TaxState, ShippingWeight, ShippingItem, ShippingPrice, Preference
from users.models import Profile
from subscriptions.models import Subscription, SubscriptionPlan


class ItemTestCase(unittest.TestCase):
    
    def setUp(self):
        # create store owner user and profile
        self.owner = User.objects.create_user("test-owner", "test-owner@mail.com", "test-owner")
        owner_profile = Profile(user=self.owner)
        owner_profile.save()

        # create a marketplace
        self.marketplace = MarketPlace(name="greatcoins", title="greatcoins", slug="greatcoins", 
                                       template_prefix="greatcoins", base_domain="greatcoins.com")
        self.marketplace.save()

        # create a shop
        self.shop = Shop(marketplace=self.marketplace, admin=self.owner, name="test_shop")
        self.shop.save()

        # create a Preference and SubscriptionPlan to shop
        Preference(shop=self.shop).save()
        self.shop.update()
        plan = SubscriptionPlan(plan_id=1,
                         marketplace=self.marketplace,
                         trial_period=True,
                         total_store_revenue=1000,
                         concurrent_store_items=1000)
        plan.save()
        Subscription(owner=owner_profile, plan=plan).save()

        # create marketplace categories and sub-categories
        self.category = MarketCategory(marketplace=self.marketplace, name="Category")
        self.category.save()
        self.subcategory = MarketSubCategory(marketplace=self.marketplace, parent=self.category, name="SubCategory")
        self.subcategory.save()

        # create a user, profile and shipping data
        self.user = User.objects.create_user("test-user", "test-user@mail.com", "test-user")
        Profile(user=self.user).save()
        shippingdata = ShippingData(first_name='User',
                                    last_name='Buyer',
                                    street_address="Calle 54",
                                    city="La Plata",
                                    state="Buenos Aires",
                                    zip="1900",
                                    country="AR")
        shippingdata.save()

        # create a shopping cart
        self.cart = Cart(shop=self.shop, bidder=self.user)
        self.cart.shippingdata = shippingdata
        self.cart.save()

    def tearDown(self):
        self.owner.delete()
        self.marketplace.delete()
        self.category.delete()
        self.subcategory.delete()
    
    def testItemCreate(self):
        import logging
        from inventory.models import Product
        products_count = Product.objects.count()
        item = Item(shop=self.shop, title="item", description="an item", 
                    price="10.0", category=self.category, subcategory=self.subcategory, 
                    qty=1, weight="2.0")
        item.save()
        
        #check Product was created
        self.assertEqual(products_count + 1, Product.objects.count())
        #check Product was deleted
        item.delete()
        self.assertEqual(products_count, Product.objects.count())

    def testSoldOut(self):
        # create a item
        item = Item(shop=self.shop,
                title="item",
                description="an item",
                price="10.0",
                category=self.category,
                subcategory=self.subcategory,
                qty=1,
                weight="2.0")
        item.save()
        
        # verify if the item is showing
        self.assertTrue(item.show)

        # add the item to cart
        self.cart.add(item, item.price, qty=1)
        self.cart.close('manual')

        # reload the item from db
        item = Item.objects.get(id=item.id)

        # verify if the item is showing and stock=0
        self.assertTrue(item.show)
        self.assertEqual(item.qty, 0)

        # change item sold_out_date and verify if the item is still showing
        past_date = datetime.datetime.now() - datetime.timedelta(days=13)
        item.sold_out_date = past_date
        item.update_show(True)
        self.assertTrue(item.show)

        # again, this time the item will not showing
        past_date = datetime.datetime.now() - datetime.timedelta(days=25)
        item.sold_out_date = past_date
        item.update_show(True)
        self.assertFalse(item.show)

        item.qty = 1
        item.save()
        self.assertTrue(item.show)

        item.qty = 0
        item.save()
        self.assertTrue(item.show)

        #
        past_date = datetime.datetime.now() - datetime.timedelta(days=25)
        item.sold_out_date = past_date
        item.update_show(True)
        self.assertFalse(item.show)
