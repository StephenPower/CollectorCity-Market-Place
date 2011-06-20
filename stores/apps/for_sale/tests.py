import unittest

from auth.models import User
from market.models import MarketPlace, MarketCategory, MarketSubCategory 
from for_sale.models import Item 
from shops.models import Shop


class LotTestCase(unittest.TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user("test", "t@t.com", "testpw")
        self.marketplace = MarketPlace(name="greatcoins", title="greatcoins", slug="greatcoins", 
                                       template_prefix="greatcoins", base_domain="greatcoins.com")
        self.marketplace.save()
        self.category = MarketCategory(marketplace=self.marketplace, name="Category")
        self.category.save()
        self.subcategory = MarketSubCategory(marketplace=self.marketplace, parent=self.category, name="SubCategory")
        self.subcategory.save()
        self.shop = Shop(marketplace=self.marketplace, admin=self.user, name="test shop")
        self.shop.save()
        

    def tearDown(self):
        self.user.delete()
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
        

