#from django.db import models
#
#from shops.models import Shop
#from market.models import MarketCategory, MarketSubCategory
#
#class Category(models.Model):
#    shop = models.ForeignKey(Shop)
#    name = models.CharField(max_length=60)
#    market_category = models.ForeignKey(MarketCategory, null=True, blank=True)
#    def __unicode__(self):
#        return self.name
#
#
#class SubCategory(models.Model):
#    shop = models.ForeignKey(Shop)
#    category = models.ForeignKey(Category)
#    market_category = models.ForeignKey(MarketSubCategory, null=True, blank=True)
#    name = models.CharField(max_length=60)
#    def __unicode__(self):
#        return self.name
#
#    