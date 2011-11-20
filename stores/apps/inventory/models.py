import datetime
import decimal

from django.db import models
from django.contrib import admin

from market.models import MarketCategory, MarketSubCategory
from shops.models import Shop

class ProductType(models.Model):
    """ 
    """
    pass


class ActiveProductsManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductsManager, self).get_query_set().filter(shop__in=Shop.actives.all())

class Product(models.Model):
    """
        Superclass for common product attrs between lots  and forsale items         
    """
    shop = models.ForeignKey(Shop)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(MarketCategory)
    subcategory = models.ForeignKey(MarketSubCategory, null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=11, decimal_places=2, default=decimal.Decimal(0))
    type = models.ForeignKey(ProductType, null=True, blank=True)
    latest_item = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    
    objects = ActiveProductsManager() # The active products manager.
    
    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        shop = self.shop
        shop.last_date_to_post = datetime.datetime.now()
        shop.save()        
    
    @classmethod
    def update_latest_item(cls, shop):
        try:
            older = Product.objects.filter(shop=shop, latest_item=True).get()
            older.latest_item = False
            older.save()
        except Product.DoesNotExist:
            pass
        
        try:
            new_latest = Product.objects.filter(shop=shop).order_by("-id")[0]
            new_latest.latest_item = True
            new_latest.save()
        except Product.DoesNotExist:
            pass
            
    def update_has_image(self):
        self.has_image = self.child().image() != None
        self.save()
    
    def child(self):
        #TODO: arreglar esto que es un asco,..
        if hasattr(self, 'lot'):
            return self.lot
        elif hasattr(self, 'item'):
            return self.item
        
        
    def __unicode__(self):
        return "%s > %s" %(self.shop, self.title)

class ProductAdmin(admin.ModelAdmin):
    list_filter = ('shop', 'date_time', 'category')

class Coin(ProductType):
    category = models.ForeignKey(MarketCategory, null=True, blank=True)
    subcategory = models.ForeignKey(MarketSubCategory, null=True, blank=True)
    country_code = models.CharField(max_length=2, default='us')
    pcgs_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(default="", blank="")
    year_issued = models.CharField(max_length=24, default="", blank="")
    actual_year = models.CharField(max_length=24, default="", blank="")
    denomination = models.CharField(max_length=60, default="", blank="")
    major_variety = models.CharField(max_length=60, default="", blank="")
    die_variety = models.CharField(max_length=60, default="", blank="")
    prefix = models.CharField(max_length=60, default="", blank="")
    suffix = models.CharField(max_length=60, default="", blank="")
    sort_order = models.CharField(max_length=60, default="", blank="")
    heading = models.CharField(max_length=60, default="", blank="")
    holder_variety = models.CharField(max_length=60, default="", blank="")
    holder_variety_2 = models.CharField(max_length=60, default="", blank="")
    additional_data = models.TextField(default="", blank="")
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Coin<%s>" % self.pcgs_number