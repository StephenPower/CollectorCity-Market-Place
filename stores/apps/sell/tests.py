import unittest
import decimal

from auth.models import User
from models import *
from for_sale.models import Item
from market.models import MarketPlace, MarketCategory, MarketSubCategory
from shops.models import Shop
from inventory.models import Product
from preferences.models import TaxState, ShippingWeight, ShippingItem, ShippingPrice

class BuyItemTestCase(unittest.TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user("test", "t@t.com", "testpw")
        self.marketplace = MarketPlace(name="greatsomething", title="Great Something", slug="great-something", 
                                       template_prefix="default", base_domain="greatsomething.com")
        self.marketplace.save()
        self.shop = Shop(marketplace=self.marketplace, admin=self.user, name="test shop")
        self.shop.save()
        self.category = MarketCategory(marketplace=self.marketplace, name="Category1")
        self.category.save()
        self.subcategory = MarketSubCategory(marketplace=self.marketplace, parent=self.category, name="SubCategory1")
        self.subcategory.save()
        self.cart = Cart(shop=self.shop, bidder=self.user)
        self.cart.save()
        
        
    def tearDown(self):
        self.user.delete()
        self.marketplace.delete()
        self.category.delete()
        self.subcategory.delete()
#        item.delete()
    
    def testCartMethods(self):
        item = Item(shop=self.shop, 
                        title="item",
                        description="an item", 
                        price="10.0", 
                        category=self.category, 
                        subcategory=self.subcategory, 
                        qty=5, 
                        weight="2.0")
        item.save()
        
        
        shippingdata = ShippingData(street_address="Calle 8 n 182", city="La Plata", state="Buenos Aires", zip="1900", country="AR")
        shippingdata.save()

        self.cart.shippingdata = shippingdata
                
        qty = item.qty
        #add an item to cart
        qty_to_buy = 2
        self.cart.add(item, item.price, qty=qty_to_buy)
        
        #check that qty item decrease in one unit
        self.assertEqual(qty, item.qty + qty_to_buy)
        
        #check that item is in cart
        cart_item = self.cart.cartitem_set.all()[0]
        self.assertEqual(item, cart_item.product)
        
        #check cart methods
        self.assertEqual(self.cart.total_items(), qty_to_buy)
        self.assertEqual(self.cart.total_weight() , decimal.Decimal("4.0"))
        self.assertEqual(self.cart.total(), decimal.Decimal("20.0"))
        self.assertEqual(self.cart.total_with_taxes(), decimal.Decimal("20.0"))
        
        #clean the cart
        self.cart.clean()
        
        #recheck cart methods
        self.assertEqual(self.cart.total_items(), 0)
        self.assertEqual(self.cart.total_weight() , decimal.Decimal("0.0"))
        self.assertEqual(self.cart.total(), decimal.Decimal("0.0"))
        self.assertEqual(self.cart.total_with_taxes(), decimal.Decimal("0.0"))
        
        
    def testTaxCalculation(self):
        item = Item(shop=self.shop, 
                title="item",
                description="an item", 
                price="10.0", 
                category=self.category, 
                subcategory=self.subcategory, 
                qty=5, 
                weight="2.0")
        item.save()
        
        #load some taxes 
        miami_tax = decimal.Decimal("2.5")
        tax_for_miami = TaxState(shop=self.shop, state="MI", tax=miami_tax)
        tax_for_miami.save()
        
        ny_tax = decimal.Decimal("1.5")
        tax_for_ny = TaxState(shop=self.shop, state="NY", tax=ny_tax)
        tax_for_ny.save()
        
        #add an item to the cart
        self.cart.add(item, item.price, qty=1)
        
        #set the shipping address        
        shippingdata = ShippingData(street_address="Abey Road", city="Great Beach", state="MI", zip="11001", country="US")
        shippingdata.save()
        self.cart.shippingdata = shippingdata
      
        #check that tax is correctly calculated
        self.assertEquals(self.cart.taxes(), miami_tax * decimal.Decimal(item.price) / decimal.Decimal("100.0"))
        self.assertNotEquals(self.cart.taxes(), ny_tax * decimal.Decimal(item.price) / decimal.Decimal("100.0"))

        #if shipping address is not MI or NY, no tax must be applied...
        shippingdata = ShippingData(street_address="Abey Road", city="Great Beach", state="IO", zip="11001", country="US")
        shippingdata.save()
        self.cart.shippingdata = shippingdata

        self.assertEquals(self.cart.taxes(), decimal.Decimal("0.0") )        
        
        
    def testShippingCharge(self):
        item = Item(shop=self.shop, 
                title="item",
                description="an item", 
                price="10.0", 
                category=self.category, 
                subcategory=self.subcategory, 
                qty=5, 
                weight="2.0")
        item.save()
        #add an item to the cart
        self.cart.add(item, item.price, qty=3)
        
        #set the shipping address        
        shippingdata = ShippingData(street_address="Abey Road", city="Great Beach", state="MI", zip="11001", country="US")
        shippingdata.save()
        self.cart.shippingdata = shippingdata
        
        sw1 = ShippingWeight(shop=self.shop, name="Shipping by Weight", price="3.00", from_weight="0.0", to_weight="5.0")
        sw1.save()
        sw2 = ShippingWeight(shop=self.shop, name="Shipping by Weight", price="5.00", from_weight="5.0", to_weight="10.0")
        sw2.save()
        self.assertEquals(self.cart.shipping_charge(), decimal.Decimal("5.0"))
        sw1.delete()
        sw2.delete()
        
        si1 = ShippingItem(shop=self.shop, name="Shipping by Item", price="9.00", from_item=0, to_item=3)
        si1.save()
        si2 = ShippingItem(shop=self.shop, name="Shipping by Item", price="19.00", from_item=3, to_item=5)
        si2.save()
        si3 = ShippingItem(shop=self.shop, name="Shipping by Item", price="29.00", from_item=5, to_item=15)
        si3.save()
        
        self.assertEquals(self.cart.shipping_charge(), decimal.Decimal("9.0"))
        si1.delete()
        si2.delete()
        si3.delete()
        
        pw1 = ShippingPrice(shop=self.shop, name="Shipping by Price", price="5.00", from_price="0.0", to_price="20.0")
        pw1.save()
        pw2 = ShippingPrice(shop=self.shop, name="Shipping by Price", price="9.00", from_price="20.0", to_price="40.0")
        pw2.save()
        self.assertEquals(self.cart.shipping_charge(), decimal.Decimal("9.0"))
        pw1.delete()
        pw2.delete()
        
        
    def testCartClose(self):
        item = Item(shop=self.shop, 
                title="item",
                description="an item", 
                price="10.0", 
                category=self.category, 
                subcategory=self.subcategory, 
                qty=2, 
                weight="2.0")
        item.save()
        
        item2 = Item(shop=self.shop, 
                title="item",
                description="an item", 
                price="10.0", 
                category=self.category, 
                subcategory=self.subcategory, 
                qty=2, 
                weight="2.0")
        item2.save()
        
        shippingdata = ShippingData(street_address="Calle 8 n 182", city="La Plata", state="Buenos Aires", zip="1900", country="AR")
        shippingdata.save()
        
        #add the shipping data
        self.cart.shippingdata = shippingdata
        self.cart.save()
        
        #add 2 items
        self.cart.add(item, item.price, qty=1)
        self.cart.add(item2, item.price, qty=2)
        
        #close the cart
        sell = self.cart.close("manual")
        
        #check that the sell object has the default values setted... 
        self.assertEquals(self.cart.total_items(), 0)
        self.assertEquals(sell.closed, False)
        self.assertEquals(sell.sellitem_set.count(), 2)
        self.assertEquals(sell.payment.state_actual.state, "PE")
        self.assertEquals(sell.shipping.state_actual.state, "PE")
        
        