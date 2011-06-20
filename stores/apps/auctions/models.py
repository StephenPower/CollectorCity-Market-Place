import datetime

from django.db import models
from shops.models import Shop
from django.utils.translation import ugettext_lazy as _


class AuctionSession(models.Model):
    shop = models.ForeignKey(Shop)
    title = models.CharField(max_length=60)
    description = models.TextField()
    start = models.DateTimeField() 
    end = models.DateTimeField()
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.title)
    
    def finished(self):
        return self.end < datetime.datetime.now()
    
    def actual(self):
        return self.end > datetime.datetime.now() and self.start < datetime.datetime.now()

    def future(self):
        return self.start > datetime.datetime.now()
    
    def status(self):
        if self.end < datetime.datetime.now():
            return _("Finished")
        elif self.end > datetime.datetime.now() and self.start < datetime.datetime.now():
            return _("Actual")
        elif self.start > datetime.datetime.now():
            return _("Future")

    def count_lots(self):
        return self.lot_set.all().count()

    @models.permalink
    def get_bidding_url(self):
        return ("bidding.views.bidding_auctions", (self.pk, ))