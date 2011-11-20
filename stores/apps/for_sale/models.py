#import datetime
import decimal
import logging

from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from core.thumbs import ImageWithThumbsField
from inventory.models import Product

#TODO: PCGSNumberException, and the Coin references in create_from_inventory must be removed from this module

PCGS_COIN_GRADING = {
    1: ('PO-1', 'Identifiable date and type'),
    2: ('FR-2', 'Mostly worn, though some detail is visible'),
    3: ('AG-3', 'Worn rims but most lettering is readable though worn'),
    4: ('G-4', 'Slightly worn rims, flat detail, peripheral lettering nearly full'),
    6: ('G-6', 'Rims complete with flat detail, peripheral lettering full'),
    8: ('VG-8', 'Design worn with slight detail'),
    10: ('VG-10', 'Design worn with slight detail, slightly clearer'),
    12: ('F-12', 'Some deeply recessed areas with detail, all lettering sharp'),
    15: ('F-15', 'Slightly more detail in the recessed areas, all lettering sharp'),
    20: ('VF-20', 'Some definition of detail, all lettering full and sharp'),
    25: ('VF-25', 'Slightly more definition in the detail and lettering'),
    30: ('VF-30', 'Almost complete detail with flat areas'),
    35: ('VF-35', 'Detail is complete but worn with high points flat'),
    40: ('EF-40', 'Detail is complete with most high points slightly flat'),
    45: ('EF-45', 'Detail is complete with some high points flat'),
    50: ('AU-50', 'Full detail with friction over most of the surface, slight flatness on high points'),
    53: ('AU-53', 'Full detail with friction over 1/2 or more of surface, very slight flatness on high points'),
    55: ('AU-55', 'Full detail with friction on less than 1/2 surface, mainly on high points'),
    58: ('AU-58', 'Full detail with only slight friction on the high points')                     
}

class PCGSNumberException(Exception):
    
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)

class Item(Product):
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    
    
    def type(self):
        return "Item"
    
    def decrease_qty(self, qty):
        self.qty = self.qty - qty
        self.save()
        if self.qty <= 0:
            #TODO: Send email to shop owner, is to expensive, should be done in a task queue...
            from sell.models import SellItem
            from django.core.urlresolvers import reverse
            
            path = "http://%s%s" % (self.shop.default_dns, reverse("bidding_view_item", urlconf="stores.urls", args=[self.id]))
            
            item_type = ContentType.objects.get_for_model(self)
            sell_items = SellItem.objects.filter(object_id=self.id, content_type__pk=item_type.id)
            total = sell_items.count()
            revenue = 0
            for sell in sell_items:
                revenue += (sell.price * sell.qty)
            msg = "There are no more Items for %s.\n\nlink: %s\n\nTotal Items Sold: %s\n\nTotal Revenue: %s\n\n\nTake notice that this last item wasn't sold yet, is currently in a cart and could be removed from it anytime. If customer decides to remove the item from the cart it will be inmediatly restored to the inventory" % (self.title, path, total, revenue)
            send_mail('Product Out Of Stock', msg, settings.EMAIL_FROM,  [self.shop.admin.email], fail_silently=True)
    
    def increase_qty(self, qty):
        self.qty = self.qty + qty
        self.save()
    
    def image(self):
        from models import ImageItem
        try:
            return ImageItem.objects.filter(item=self).filter(primary_picture=True).get()
        except ImageItem.DoesNotExist:
            pass
        
        try:
            img = ImageItem.objects.filter(item=self)[0]
            img.primary_picture = True
            img.save()
            return img
        except IndexError:
            return None
    
    @models.permalink
    def get_bidding_url(self):
        return ("bidding.views.bidding_view_item", (self.pk, ))

            
    @classmethod
    def create_from_inventory(cls, shop, properties, values):
        """ 
        Creates an Item from the file inventory 
        
        @param properties = [DealerProductNumber, PCGSNumber, GradingService, Grade, Quantity, RetailPrice, WholesalePrice, ProductDescription, ImageURL1, ImageURL2 ]
        @param values = ['F22-014', '2067', 'PCGS', '64', '1', '600', '', '1863 Snow-1. Repunched date 18/18. MS-64 PCGS (PS). Eagle Eye Photo Seal. The coin is well struck with even coloration. There are a few light marks but nothing out of the ordinary for the grade.', 'http://www.indiancent.com/img/p/751-1297-thickbox.jpg', 'http://www.indiancent.com/img/p/751-1298-thickbox.jpg'] 
        """
        from inventory.models import Coin
        
        vals = {}
        for property in properties:
            vals[property] = values[properties.index(property)]
        
        grading_service = vals['GradingService']
        grade = int(decimal.Decimal(vals['Grade']))
        grading_coin_number = int(decimal.Decimal(vals['PCGSNumber']))
        dealer_coin_number = vals['DealerProductNumber']
        
        images = []
        images.append(vals['ImageURL1'])
        images.append(vals['ImageURL2'])
        
        item = Item(shop=shop)
        
        
        try:
            coin = Coin.objects.filter(pcgs_number=grading_coin_number).get()
            item.category = coin.category
            item.subcategory = coin.subcategory
            #Date Type Grade Grading Companie
            #1857 Cent Flying Eagle MS63 PCGS"
            # Date, Mintmark (as 1935-D) grade (as MS-65RD NGC
            #item.title = "%s, Grade: %s (%s), Price: %s" % (coin.description, grade, grading_service, vals['RetailPrice'])
            prefix = coin.prefix.upper()
            suffix = coin.suffix.upper()
            
            if prefix == 'MS' and grade <= 58:
                try:
                    pcgs_grade = PCGS_COIN_GRADING[grade][0]
                except KeyError:
                    pcgs_grade = 'MS %s' % grade
                    
                item.title = "%s %s%s %s" % (coin.year_issued, 
                                                pcgs_grade,
                                                suffix,
                                                grading_service.upper().strip())
                
            else: 
                item.title = "%s %s-%s%s %s" % (coin.year_issued, 
                                                prefix,
                                                grade, 
                                                suffix,
                                                grading_service.upper().strip())
        except Coin.DoesNotExist:
            raise PCGSNumberException("Invalid pcgs number: %s" % grading_coin_number)
        
        item.description = vals['ProductDescription']
        item.price = vals['RetailPrice']
        item.qty = int(decimal.Decimal(vals['Quantity']))
        item.weight = decimal.Decimal('0.0')
        item.save()
        #TODO: Sacar esto afuera para que se haga una sola vez
        Item.update_latest_item(shop)
        
        #Queue images to get
        for url in images:
            ImageItemURLQueue(item=item, url=url).save()
            
        return item
        
    def has_stock(self):
        return self.qty > 0

    def activate(self):
        pass
    

class ItemAdmin(admin.ModelAdmin):
    list_filter = ('price', 'qty')
    
class ImageItem(models.Model):
    #image = models.ImageField(upload_to='images') 
    image = ImageWithThumbsField(upload_to='images', sizes=((100,100),(400,400)), crop=False)
    item = models.ForeignKey(Item)
    primary_picture = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "%s > %s" % (self.item, self.id)

    def save(self, *args, **kwargs):
        super(ImageItem, self).save(*args, **kwargs)
        self.item.has_image = True
        self.item.save()
        

class ImageItemURLQueue(models.Model):
    item = models.ForeignKey(Item) 
    url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_image(self):
        import httplib2
        from urlparse import urlparse
        
        try:
            name = urlparse(self.url).path.split('/')[-1]
            http = httplib2.Http()
            status, content = http.request(self.url)
            response = status["status"]
            if response == "200":
                imageItem = ImageItem(item=self.item)                
                imageItem.image.save(name, ContentFile(content), save=True)
            else:
                logging.error("Could not charge image %s. status=%s" % (name, response))
        except Exception,e:
            logging.error("Could not charge image %s. %s" % (name, e))
            
        self.delete()



