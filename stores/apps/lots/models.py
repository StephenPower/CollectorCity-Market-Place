import datetime
import decimal

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from auth.models import User
#from shops.models import Shop
from auctions.models import AuctionSession
from core.thumbs import ImageWithThumbsField
from inventory.models import Product
from market.models import MarketCategory, MarketSubCategory
from django.template.defaultfilters import striptags

LOT_TYPE = [('S',_('Standard')),('B', _('Buy Now'))]

STATE_ITEM = [
    ('A', _('Active sale')),
    ('S', _('Sold')),
    ('N', _('Did not sell')),
]


class Lot(Product):
    starting_bid = models.DecimalField(max_digits=11, decimal_places=2)
    reserve = models.DecimalField(max_digits=11, decimal_places=2)
    session = models.ForeignKey(AuctionSession)
    state = models.CharField(max_length=1, choices=STATE_ITEM, default='A')
    bid_actual = models.OneToOneField('BidHistory', null=True, related_name="lot_history")
    
    def __unicode__(self):
        return "%s > %s" % (self.session, self.title)

    @models.permalink
    def get_bidding_url(self):
        return ("bidding.views.bidding_view_lot", (self.pk, ))
        

    def image(self):
        from models import ImageLot
        try:
            return ImageLot.objects.filter(lot=self).filter(primary_picture=True).get()
        except ImageLot.DoesNotExist:
            pass
        
        try:
            img = ImageLot.objects.filter(lot=self)[0]
            img.primary_picture = True
            img.save()
            return img
        except IndexError:
            return None
 

    def count_bids(self):
        return self.bidhistory_set.all().count()    

    def count_bidders(self):
        return BidHistory.objects.filter(lot = self).values("bidder").distinct().count()

    def bids(self):
        return self.bidhistory_set.all()    
    
    def time_left(self):
        if self.session.end < datetime.datetime.now():
            return _("Finish")
        time = self.session.end - datetime.datetime.now()
        days = time.days
        s = time.seconds
        hours = s // 3600 
        s = s - (hours * 3600)
        minutes = s // 60
        #seconds = s - (minutes * 60)
        if days > 0:
            result = '%sd %sh' % (days, hours)
        elif hours > 0:
            result = '%sh %sm' % (hours, minutes)
        else:
            result = '%sm' % minutes
        return result
    
    def time_left_long(self):
        if self.session.end < datetime.datetime.now():
            return _("Finish")
        time = self.session.end - datetime.datetime.now()
        days = time.days
        s = time.seconds
        hours = s // 3600 
        s = s - (hours * 3600)
        minutes = s // 60
        #seconds = s - (minutes * 60)
        if days > 0:
            result = '%s days %s hours %s mins' % (days, hours, minutes)
        elif hours > 0:
            result = '%s hours %s mins' % (hours, minutes)
        else:
            result = '%s mins' % minutes
        return result
    
    
    def current_bid(self):
        if self.bid_actual:
            return self.bid_actual.bid_amount
        else:
            return self.starting_bid

    def price(self):
        return self.current_bid()
        
    def next_bid_from(self):
        if self.bid_actual:
            actual_bid = self.bid_actual.bid_amount
            amount = BidderIncrementCalculator().get_next_bid_for(actual_bid)
            return amount
        else:
            return self.starting_bid

    def is_active(self):
        return self.state == 'A'
    
    def is_sold(self):
        return self.state == 'S'
    
    def is_didnt_sell(self):
        return self.state == 'N'
    
    def decrease_qty(self, qty):
        pass
    
    def increase_qty(self, qty):
        pass

    def activate(self):
        self.state = 'A'
        self.save()
    
#    def is_standard(self):
#        return self.lot_type == 'S'

#    def is_buy_now(self):
#        return self.lot_type == 'B'

    def history(self):
        return BidHistory.objects.filter(lot=self).order_by('-bid_time')
    
#    def buy_now(self, bidder, amount):
#        bid_history = BidHistory(lot=self, bidder=bidder, bid_amount=amount)
#        bid_history.save()
#        
#        self.state = 'S'
#        self.bid_actual = bid_history
#        self.save() 
#        
#        Payment.new_pending_payment(self.shop, bidder, self)

    def bid(self, bidder, amount, ip):
        bid_history = BidHistory(lot=self, bidder=bidder, bid_amount=amount, request_ip=ip)
        bid_history.save()
        self.bid_actual = bid_history
        self.save()
        
        self.shop.bids += 1
        self.shop.save() 
        
    def sold(self):
        from sell.models import Cart
        from preferences.models import EmailNotification
        from django.core.mail import send_mail    
        from django.template import Context, Template
        
        self.state = 'S'
        self.save()
        cart = Cart.objects.filter(shop=self.shop, bidder=self.bid_actual.bidder).get()
        cart.add(self, self.current_bid(), 1)
        
        # ------------------------------------------------------------------------
        # Send an email to bidder to notify he/she has won the auction
        c = Context({'bidder_name': self.bid_actual.bidder.get_full_name(),
                     'bid_amount': self.bid_actual.bid_amount,
                     'bid_time': self.bid_actual.bid_time,
                     'shop': self.shop.name,
                     'session_title': self.session.title,
                     'session_description': striptags(self.session.description),
                     'session_start': str(self.session.start),
                     'session_end': str(self.session.end),
                     'lot_title': self.title,
                     'lot_description': striptags(self.description) })
        
        try:
            notification = EmailNotification.objects.filter(type_notification='AWC', shop=self.shop).get()
            subj_template = Template(notification.subject)
            body_template = Template(notification.body)
            
            subj_text = subj_template.render(c)
            body_text = body_template.render(c)
            send_mail(subj_text, body_text, 'no-reply@greatcoins.com',  [self.bid_actual.bidder.email], fail_silently=True)
            
        except EmailNotification.DoesNotExist:
            msg = "You made a bid u$s %s for %s and have won the auction!. Please contact %s to get more details about this purchase. Thanks" % (self.bid_actual.bid_amount, self.title, self.shop.admin.email)
            send_mail("Congratulations!!", msg, 'no-reply@greatcoins.com',  [self.bid_actual.bidder.email], fail_silently=True)
            
        except Exception, e:
            from django.conf import settings
            send_mail("Could not send email to lot winner!", "Message could not be delivered to %s" % self.bid_actual.bidder.email, 'no-reply@greatcoins.com',  [mail for (name, mail) in settings.ADMINS], fail_silently=True)         
        
    
    def didnt_sell(self):
        self.state = 'N'
        self.save()
        

    def sell_actual(self):
        from sell.models import SellItem
        sell_type = ContentType.objects.get_for_model(self)
        try:
            sell_item = SellItem.objects.filter(object_id=self.id,
                                                    content_type__pk=sell_type.id).get()
            return sell_item.sell
        except:
            return None    

    def reserve_has_been_met(self):
        if self.bid_actual is None: return False
        return self.current_bid() >= self.reserve 

#        
#        Payment.new_pending_payment(self.shop, self.bid_actual.bidder, self)
        
#    def payment(self):
#        #TODO Check relation one to one?
#        try:
#            return self.payment_set.get()
#        except:
#            return None
#        
#
#    def shipping(self):
#        #TODO Check relation one to one?
#        try:
#            return self.shipping_set.get()
#        except:
#            return None

    
class ImageLot(models.Model):
    image = ImageWithThumbsField(upload_to='images', sizes=((100,100),(400,400)), crop=False)
    lot = models.ForeignKey(Lot)
    primary_picture = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        super(ImageLot, self).save(*args, **kwargs)
        self.lot.has_image = True
        self.lot.save()


class BidHistory(models.Model):
    lot = models.ForeignKey(Lot)
    bidder = models.ForeignKey(User)
    bid_amount = models.DecimalField(max_digits=11, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    request_ip = models.CharField(max_length=15, default="0.0.0.0")
    
    def __unicode__(self):
        return "%s > %s (%s)" % (self.lot, self.bidder, self.bid_amount)


class BidderIncrementCalculator:
    
    def __init__(self):
        self.table = [
            (decimal.Decimal("0.01"), decimal.Decimal("0.99"), decimal.Decimal("0.05")),
            (decimal.Decimal("1.00"), decimal.Decimal("4.99"), decimal.Decimal("0.25")),
            (decimal.Decimal("5.00"), decimal.Decimal("24.99"), decimal.Decimal("0.50")),
            (decimal.Decimal("25.00"), decimal.Decimal("99.99"), decimal.Decimal("1.00")),
            (decimal.Decimal("100.00"), decimal.Decimal("249.99"), decimal.Decimal("2.50")),
            (decimal.Decimal("250.00"), decimal.Decimal("499.99"), decimal.Decimal("5.00")),
            (decimal.Decimal("500.00"), decimal.Decimal("999.99"), decimal.Decimal("10.00")),
            (decimal.Decimal("1000.00"), decimal.Decimal("2499.99"), decimal.Decimal("25.00")),
            (decimal.Decimal("2500.00"), decimal.Decimal("4999.99"), decimal.Decimal("50.00")),
            (decimal.Decimal("5000.00"), decimal.Decimal("99999.99"), decimal.Decimal("100.00")),
        ]
    
    def get_next_bid_for(self, actual):
        for limit in self.table:
            (from_price, to_price, inc) = limit
            if actual >= from_price and actual <= to_price: return actual + inc
        
        return actual + inc
    
    def match_for(self, amount):
        last_limit = None
        for limit in self.table:
            (from_price, to_price, inc) = limit
            if amount >= from_price and amount <= to_price: return limit
            last_limit = limit
            
        return last_limit
        
#class BidIncrementAmount(models.Model):
#    from_price = models.DecimalField(max_digits=11, decimal_places=2)
#    to_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
#    bid_increment = models.DecimalField(max_digits=11, decimal_places=2)