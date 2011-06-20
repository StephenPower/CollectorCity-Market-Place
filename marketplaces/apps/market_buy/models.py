from django.db import models
from django.conf import settings

from market.models import MarketPlace, MarketCategory, MarketSubCategory
from auth.models import User

class WishListItem(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    posted_on = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User)
    ideal_price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(MarketCategory)
    subcategory = models.ForeignKey(MarketSubCategory, blank=True, null=True)
    public = models.BooleanField(default=False)
    def __str__(self):
        return "%s - %s" % (self.marketplace, self.description)

class Show(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    name = models.CharField(max_length=128)
    date_from = models.DateField()
    date_to = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=128) 
    country = models.CharField(max_length=128, default="US")
    state = models.CharField(max_length=128)
    zip = models.CharField(max_length=10)
    contact_info = models.CharField(max_length=128)
    admission = models.DecimalField(max_digits=11, decimal_places=2, default="0.0")
    location = models.CharField(max_length=255, default="49.00, -96.00")
    def is_active(self):
        import datetime
        today = datetime.datetime.today()
        return today < self.date_to
    
    def duration(self):
        dif = self.date_to - self.date_from
        return dif.days
        
    def __str__(self):
        return "%s > %s (%s)" % (self.marketplace, self.name, self.city)
    
    def save(self):
        from geopy import geocoders
        super(Show, self).save()
        try:
            g = geocoders.Google(settings.GOOGLE_KEY)
            place = "%s, %s, %s, %s" % (self.address, self.city, self.state, self.country)
            place, point = g.geocode(place)
            self.location = "%s,%s" % point
            super(Show, self).save()
        except:
            pass
        
    def geo_location(self):
        return self.location.split(",")  

    def will_go_show(self, shop):
        from shops.models import DealerToShow
        try:
            DealerToShow.objects.filter(shop=shop, show=self).get()
            return True
        except DealerToShow.DoesNotExist:
            return False 
            
        
#TODO: change to EditorProductPick
class EditorPick(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    order = models.IntegerField(default=5)
    product = models.ForeignKey("inventory.Product")
    def __str__(self):
        return "%s > %s (%s)" % (self.marketplace, self.product, self.order)

class MarketPlacePick(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    order = models.IntegerField(default=5)
    product = models.ForeignKey("inventory.Product")
    def __str__(self):
        return "%s > %s (%s)" % (self.marketplace, self.product, self.order)
    
class DealerPick(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    order = models.IntegerField(default=5)
    shop = models.ForeignKey("shops.Shop")
    description = models.TextField(default="Dealer description here")
    def __str__(self):
        return "%s > %s (%s)" % (self.marketplace, self.shop, self.order)
    
class BestSeller(models.Model):
    shop = models.ForeignKey("shops.Shop")
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    revenue = models.DecimalField(max_digits=11, decimal_places=2)
    def __str__(self):
        return "%s > %s" % (self.shop, self.revenue)