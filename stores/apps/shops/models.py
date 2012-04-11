import logging

from django.conf import settings 
from django.db import models
from django.db.models import Q
from django.contrib import admin

from auth.models import User 
from market.models import MarketPlace
from market_buy.models import Show

from payments.gateways.braintreegw import BraintreeGateway

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
    
class ActiveShopManager(models.Manager):
    
    def get_query_set(self):
        return super(ActiveShopManager, self).get_query_set().filter(active=True)
    

class Shop(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    admin = models.ForeignKey(User)
    name = models.CharField(max_length=60)
    date_time = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    bids = models.IntegerField(default=0)
    location = models.CharField(max_length=255, default="39.29038,-76.61219")
    last_date_to_post = models.DateTimeField(blank=True, null=True)
    last_date_to_change_layout = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True) 
    objects = ShopManager()
    actives = ActiveShopManager()
    
    def save(self, *args, **kwargs):
        if self.subscription():
            self.active = self.subscription().status == "A"
        super(Shop, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.name.capitalize()
    
    def delete(self, *args, **kwargs):
        status = self.subscription().status
        if status == "A":
            raise Exception("This shop can't be deleted because it has an active subscription")
        else:
            super(Shop, self).delete(*args, **kwargs)
    
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
    
    def billing_info(self):
        try:
            info = self.shopbillinginfo_set.all()[0]
            return info 
        except Exception:
            return None
        
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
            return Post.objects.filter(shop=self).filter(draft=False).order_by('-date_time')[0]
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
    
    def last_date_to_post_item(self):
        from inventory.models import Product
        
        if self.last_date_to_post is None:
            try: 
                product = Product.objects.filter(shop=self, latest_item=True).get()
                self.last_date_to_post = product.date_time
                self.save()                
            except:
                return None
        
        return self.last_date_to_post
    
    def total_items(self):
        from for_sale.models import Item
        return Item.objects.filter(shop=self).count()
    
    def total_products(self):
        from inventory.models import Product
        return Product.objects.filter(shop=self).count()
    
    def total_transactions(self):
        from sell.models import Sell
        return Sell.objects.filter(shop=self, shop__marketplace=self.marketplace).count()
    
    def categories_list(self):
        return sorted(set(map(lambda product: product.category, self.product_set.filter(Q(item__qty__gt=0)|Q(lot__isnull=False)).select_related('category'))), key=lambda category: category.name)
    
    def sub_categories_list(self):
        return sorted(set(map(lambda product: product.subcategory, self.product_set.filter(Q(subcategory__isnull=False),Q(item__qty__gt=0)|Q(lot__isnull=False)).select_related('subcategory'))), key=lambda category: category.name)

    def categories_total(self):
        return len(set(map(lambda product: product.category, self.product_set.filter(Q(item__qty__gt=0)|Q(lot__isnull=False)).select_related('category'))))
    
    def sub_categories_total(self):
        return len(set(map(lambda product: product.subcategory, self.product_set.filter(Q(subcategory__isnull=False),Q(item__qty__gt=0)|Q(lot__isnull=False)).select_related('subcategory'))))

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
        from django.core.exceptions import MultipleObjectsReturned
        
        profile = self.owner().get_profile()
        try:
            subscription = Subscription.objects.filter(owner=profile).get()
        except MultipleObjectsReturned:
            msg = "It seems that there is more that one subscription for this profile: %s. This should never have happened!" % profile
            logging.critical(msg)
            subscription = Subscription.objects.filter(owner=profile)[0]
        except Exception, e:
            msg = "An exception occurred when trying to get the shop subscription for this shop: %s. %s" % (self, e)
            logging.critical(msg)
            subscription = None
            
        return subscription
    
    def plan(self):
        return self.subscription().plan
    
    def get_main_menu_links(self):
        menus = self.menu_set.all()
        links = []
        if menus.count() > 0:
            for link in menus[0].links():
                if link.to == "/auctions/" and not self.auctions_feature_enabled():
                    continue
                links.append(link)
        return links    
    
    #Getters for Enabled/Disabled Features
    def get_features(self):
        from subscriptions.models import Feature
        features = None
        try:
            features = Feature.objects.filter(shop=self).get()
        except Feature.DoesNotExist:
            plan = self.plan()
            features = Feature(shop=self)
            features.auctions = True if plan.create_auctions == 0 else False 
            features.wishlist = True if plan.community_wish_list == 0 else False
            features.mailinglist = True if plan.collect_emails == 0 else False
            features.google_analytics = True if plan.google_analytics_support == 0 else False
            features.show_attendance = True if plan.show_attendance == 0 else False
            features.custom_dns = True if plan.custom_domain_name_fee == 0 else False
            features.theme_change = True if plan.theme_change == 0 else False
            features.add_new_pages = True if plan.add_new_pages == 0 else False
            
            if plan.payment_methods >= 1:
                features.paypal = True
            if plan.payment_methods >= 2:
                features.google_checkout = True 
            if plan.payment_methods >= 3:
                features.credit_card = True
            if plan.payment_methods == 4:
                features.manual_payment = True
            
            features.save()
    
        return features
    
    def get_help_text_support(self):
        from support.models import FeaturesHelpText
        help = None
        try:
            help = FeaturesHelpText.objects.all()[0]
        except Exception:
            help = FeaturesHelpText()
            help.save()
        return help
    
    def add_pages_feature_enabled(self):
        return self.get_features().add_new_pages        
    
    def add_pages_feature_price(self):
        return self.plan().add_new_pages
    
    def add_pages_feature_help_text(self):
        return self.get_help_text_support().add_new_pages
    
    def auctions_feature_enabled(self):
        return self.get_features().auctions        
    
    def auctions_feature_price(self):
        return self.plan().create_auctions
    
    def auctions_feature_help_text(self):
        return self.get_help_text_support().auctions
    
    def wishlist_feature_enabled(self):
        return self.get_features().wishlist
    
    def wishlist_feature_price(self):
        return self.plan().community_wish_list
    
    def wishlist_feature_help_text(self):
        return self.get_help_text_support().wishlist
    
    def mailinglist_feature_enabled(self):
        return self.get_features().mailinglist
    
    def mailinglist_feature_price(self):
        return self.plan().collect_emails
    
    def mailinglist_feature_help_text(self):
        return self.get_help_text_support().mailinglist
    
    def analytics_feature_enabled(self):
        return self.get_features().google_analytics
    
    def analytics_feature_price(self):
        return "10.00"
    
    def analytics_feature_help_text(self):
        return self.get_help_text_support().google_analytics
    
    def additional_payment_feature_price(self):
        return self.plan().additional_payment_price
    
    def shows_feature_enabled(self):
        return self.get_features().show_attendance
    
    def shows_feature_price(self):
        return self.plan().show_attendance
    
    def shows_feature_help_text(self):
        return self.get_help_text_support().show_attendance
        
    def dns_feature_enabled(self):
        return self.get_features().custom_dns
    
    def dns_feature_price(self):
        return self.plan().custom_domain_name_fee
    
    def dns_feature_help_text(self):
        return self.get_help_text_support().custom_dns    
    
    def paypal_feature_enabled(self):
        return self.get_features().paypal
    
    def theme_change_enabled(self):
        return self.get_features().theme_change
    
    def credit_card_feature_enabled(self):
        return self.get_features().credit_card
    
    def manual_payment_feature_enabled(self):
        return self.get_features().manual_payment
    
    def google_checkout_feature_enabled(self):
        return self.get_features().google_checkout    
    
    def theme_change_feature_enabled(self):
        return self.get_features().theme_change
    
    def theme_change_feature_price(self):
        return self.plan().theme_change
    
    def voice_support_price(self):
        return self.plan().voice_support_price
    
    def email_support_price(self):
        return self.plan().email_support_price    
    
    
class ShopBillingInfo(models.Model):
    shop = models.ForeignKey(Shop)
    #card_ending = models.CharField(max_length=60, default = "Card ending")
    #card_expire = models.DateTimeField()
    customer_id = models.CharField(max_length=60, default="undefined", help_text="The Braintree CustomerID")
    street = models.CharField(max_length=60, default = "Street")
    zip = models.CharField(max_length=30, default = "Zip")
    city = models.CharField(max_length=60, default = "City")
    state = models.CharField(max_length=60, default = "State")
    
    def __str__(self):
        return "%s (%s)" % (self.shop, self.customer_id)
    
    def credit_card(self):
        
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        customer = None
        cc_bean = {}
        try:
            customer = gw.get_customer_details(self.customer_id)
            cc = customer.credit_cards[0]
            cc_bean['card_type'] = cc.card_type
            cc_bean['expiration_date'] = cc.expiration_date
            cc_bean['masked_number'] = "************" + cc.masked_number[12:]
            cc_bean['expired'] = cc.is_expired
            cc_bean['token'] = cc.token
        except Exception, e:
            logging.critical(e)
        return cc_bean
    
    def update_customer_id(self):
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        try:
            subscription_id = self.shop.subscription().subscription_id
        except:
            logging.critical("Could not update Customer ID for shop %s" % self.shop)
            return
        
        subs = gw.get_subscription_details(subscription_id)
        cid = subs.transactions[0].customer_details.id
        self.customer_id = cid
        self.save()
        logging.critical("Billing info Customer ID for shop %s updated" % self.shop)        
        
    
class DealerToShow(models.Model):
    shop = models.ForeignKey(Shop)
    show = models.ForeignKey(Show)

class MailingListMember(models.Model):
    shop = models.ForeignKey(Shop)
    email = models.EmailField()

    def __unicode__(self):
        return u'%s > %s' %(self.shop.name, self.email)
