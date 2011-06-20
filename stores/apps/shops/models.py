import logging

from django.conf import settings 
from django.db import models
from django.contrib import admin

from auth.models import User 
from market.models import MarketPlace
from market_buy.models import Show

class ShopManager(models.Manager):
    
    def create(self, marketplace, name, admin, name_store):
        
        from geopy import geocoders
        from themes.models import Theme
        from preferences.models import Preference, DnsShop
        from blog_pages.models import Home, About, Menu, DynamicPageContent
        from themes.models import PAGES
        
        shop = Shop(marketplace=marketplace, name=name, admin=admin)
        
        profile = admin.get_profile()
        try:
            #get the geoposition according to the shop address
            g = geocoders.Google(settings.GOOGLE_KEY)
            place = "%s, %s, %s, %s" % (profile.street_address, profile.city, profile.state, profile.country)
            place, point = g.geocode(place)
            shop.location = "%s,%s" % point
        except Exception, e:
            logging.critical(e)
        
        shop.save()

        Theme.create_default(shop)
        
        """ Create Static Pages for this shop """
        Home(shop=shop).save()
        About(shop=shop).save()
        
        """ Create Content for Dynamic Pages for this shop """        
        for page in PAGES:
            DynamicPageContent(shop=shop, page=page, meta_content=page).save()
            
        """ Create Default MENU """
        Menu.create_default(shop)
            
        """ Create DNS default """
        dns = DnsShop(shop=shop, dns="%s.%s" % (shop.name, settings.DEFAULT_DNS), default=True)
        dns.save()
            
        """ Create preference to shop """
        preference = Preference(shop=shop, name_store=name_store)
        preference.save()
        
        
        return shop


class Shop(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    admin = models.ForeignKey(User)
    name = models.CharField(max_length=60)
    date_time = models.DateTimeField(auto_now_add=True)

    views = models.IntegerField(default=0)
    bids = models.IntegerField(default=0)
    location = models.CharField(max_length=255, default="39.29038,-76.61219")
    
    objects = ShopManager()
    
    def delete(self, *args, **kwargs):
        status = self.subscription().status
        if status == "A":
            raise Exception("This shop can't be deleted because it has an active subscription")
        else:
            super(Shop, self).delete(*args, **kwargs)        
            
    
    def __unicode__(self):
        return self.name.capitalize()
    
    @property
    def default_dns(self):
        """
        Builds the default dns name of the shop
        #FIXME: remember to update this once we create the marketplace
        """
        from preferences.models import DnsShop
        try:
            dns = DnsShop.objects.filter(shop=self, default=True).get()
        except DnsShop.DoesNotExist:
            try:
                dns = DnsShop.objects.filter(shop=self)[0]
                dns.default = True
                dns.save()
            except IndexError:
                dns = DnsShop(shop=self, dns="%s.%s" % (self.name, settings.DEFAULT_DNS), default=True)
                dns.save()
        return dns.dns
    
    def owner(self):
        return self.admin
    
    def is_admin(self, user):
        #TODO: Reimplement when shop have more that one admin...
        return self.admin == user 
        
    def name_shop(self):
        try:
            return self.preference_set.all().get().name_store.title()
        except:
            return "Shop"
    
    def add_view(self):
        self.views += 1
        self.save()
        
    #TODO: borrar, y poner oneToOne la relacion de preferencia con el shop
    def page(self):
        return self.page_set.all()[0]

    #TODO: borrar, y poner oneToOne la relacion de preferencia con el shop
    def preference(self):
        from preferences.models import Preference
        preferences = Preference.objects.filter(shop=self).get()
        return preferences

    def first_post(self):
        from blog_pages.models import Post
        try:
            return self.post_set.all()[0]
        except:
            post = Post(shop=self, title="First Post", body="""This is your blog. 
            You can use it to write about new product launches, experiences, 
            tips or other news you want your costumers to read about.""")
            post.save()
            return post
        
    def last_post(self):
        from blog_pages.models import Post
        try:
            return Post.objects.filter(shop=self).order_by('-date_time')[0]
        except:
            return None
    
    
    def theme(self):
        try:
            return self.preference_set.all().get().theme.name
        except:
            return 'default'

    def update_page_content(self):
        """ Creates DynamicPageContent for those old shops """
        from themes.models import PAGES
        from blog_pages.models import DynamicPageContent
        for page in PAGES:
            try:
                DynamicPageContent.objects.filter(shop=self, page=page).get()
            except DynamicPageContent.DoesNotExist:
                logging.debug("Creating page %s for %s" % (page, self))
                DynamicPageContent(shop=self, page=page, meta_content=page).save()
            
    def update(self):
        """ Create Blog Page to shop """
        from blog_pages.models import Home, About, Menu
        from themes.models import Theme
                
        try:
            Home.objects.filter(shop=self).get()
        except Home.DoesNotExist:
            Home(shop=self).save()
            
        try:
            About.objects.filter(shop=self).get()
        except About.DoesNotExist:
            About(shop=self).save()
        Menu.create_default(self)

        """ Create default pages whit default theme """
        
        #Theme.create_default(self)

    def last_posted_products(self):
        from inventory.models import Product 
        products = Product.objects.filter(shop=self, latest_item=False) 
        if products.count < 5:
            return products
        else:
            products = products.order_by('-date_time')[:5]
            return products

    def geo_location(self):
        return self.location.split(",")
    
    def update_geolocation(self):
        
        from geopy import geocoders
        try:
            profile = self.owner().get_profile()
            g = geocoders.Google(settings.GOOGLE_KEY)
            place = "%s, %s, %s, %s" % (profile.street_address, profile.city, profile.state, profile.country)
            place, point = g.geocode(place)
            self.location = "%s,%s" % point
            self.save()
            logging.info("shop %s updated" % self)
        except Exception, e:
            logging.info("shop %s location could not be updated because %s" % (self, e))
    
    def get_limit(self, key):
        return self.plan().get_limit(key)
    
    def subscription(self):
        from subscriptions.models import Subscription
        profile = self.owner().get_profile()
        subscription = Subscription.objects.filter(owner=profile).get()
        return subscription
    
    def is_active(self):
        return self.subscription().status == "A"
    
    def plan(self):
        return self.subscription().plan
    
class ShopBillingInfo(models.Model):
    shop = models.ForeignKey(Shop)
    card_ending = models.CharField(max_length=60, default = "Card ending")
    card_expire = models.DateTimeField()
    street = models.CharField(max_length=60, default = "Street")
    zip = models.CharField(max_length=30, default = "Zip")
    city = models.CharField(max_length=60, default = "City")
    state = models.CharField(max_length=60, default = "State")

class DealerToShow(models.Model):
    shop = models.ForeignKey(Shop)
    show = models.ForeignKey(Show)

class MailingListMember(models.Model):
    shop = models.ForeignKey(Shop)
    email = models.EmailField()
    
