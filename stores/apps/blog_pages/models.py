import re
from django.db import models
from shops.models import Shop


class Post(models.Model):
    shop = models.ForeignKey(Shop)
    title = models.CharField(max_length=60)
    body = models.TextField()
    meta_content = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    draft = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.title)
    
    def visited(self):
        self.views = self.views + 1
        self.save()
        
    def month(self):
        return self.date_time.strftime("%B %Y")
    
    def publish(self, value):
        self.draft = not(value)
        self.save()
        
    @models.permalink
    def get_bidding_url(self):
        return ("bidding.views.bidding_view_post", (self.pk, ))

class Home(models.Model):
    shop = models.OneToOneField(Shop)
    title = models.CharField(max_length=60, default="Welcome to My Store")
    body = models.TextField(default="This text will be shown in the home page as a 'Welcome Text'. Also you can add a picture to accompany the text.")
    meta_content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True) 
    last_updated =  models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.title)


class About(models.Model):
    shop = models.OneToOneField(Shop)
    title = models.CharField(max_length=60, default="About Us")
    body = models.TextField(default="This is where you may put a little description about you and your activity.")
    meta_content = models.TextField(blank=True, null=True)
    last_updated =  models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.title)    
    
class Page(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=60) 
    name_link = models.CharField(max_length=60)
    title = models.CharField(max_length=60)
    body = models.TextField()
    meta_content = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)
    def __unicode__(self):
        return "%s > Page: %s" % (self.shop, self.name)
    
    def delete(self):
        """
            This delete the links related to the page
        """
        links = Link.objects.filter(menu__shop=self.shop, to='/pages/%s/' % self.name_link)
        for l in links:
            l.delete()
        super(Page, self).delete()

    @models.permalink
    def get_bidding_url(self):
        return ("bidding.views.pages", (self.pk, ))
    
class PageVersion(models.Model):
    page = models.ForeignKey(Page)
    name = models.CharField(max_length=60) 
    name_link = models.CharField(max_length=60)
    title = models.CharField(max_length=60)
    body = models.TextField()
    meta_content = models.TextField(blank=True, null=True)
    save_on = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-save_on"]
        
    def __unicode__(self):
        return "%s" % (self.save_on)
    
class DynamicPageContent(models.Model):
    shop = models.ForeignKey(Shop)
    page = models.CharField(max_length=100)
    meta_content = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return "%s > Page: %s" % (self.shop, self.page)

class Menu(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=60)
    def __unicode__(self):
        return "%s > %s" % (self.shop, self.name)
    
    @classmethod
    def create_default(cls, shop): 
        try:
            Menu.objects.filter(shop=shop, name="Main Menu").get()
        except Menu.DoesNotExist:
            menu = Menu(name="Main Menu")
            menu.shop = shop
            menu.save()
            link_home = Link(name = "Home", to='/home/', title='', menu=menu, order=1)
            link_home.save()
            link_auctions = Link(name = "Auctions", to='/auctions/', title='', menu=menu, order=2)
            link_auctions.save()
            link_for_sale = Link(name = "For Sale", to='/for_sale/', title='', menu=menu, order=3)
            link_for_sale.save()
            link_blog = Link(name = "Blog", to='/blog/', title='', menu=menu, order=4)
            link_blog.save()
            link_about_us = Link(name = "About Us", to='/about_us/', title='', menu=menu, order=5)
            link_about_us.save()
        try:
            Menu.objects.filter(shop=shop, name="Footer").get()
        except Menu.DoesNotExist:
            footer = Menu(name="Footer")
            footer.shop = shop
            footer.save()
            link_search = Link(name = "Search", to='/search/', title='', menu=footer, order=1)
            link_search.save()
            link_about_us = Link(name = "About Us", to='/about_us/', title='', menu=footer, order=2)
            link_about_us.save()
         
    def links(self):
        return Link.objects.filter(menu=self).order_by('order')
    
    
class Link(models.Model):
    """ 
        Return if the page is visible, if page not exsist return True, 
        at this case the page is Home or About
    """
    
    name = models.CharField(max_length=60)
    to = models.CharField(max_length=120)
    title = models.CharField(max_length=60)
    menu = models.ForeignKey(Menu)
    order = models.PositiveIntegerField()
    def __unicode__(self):
        return self.name
    
    def visible(self):
        try:
            page = Page.objects.filter(name_link=re.sub(r'\/([pages]*)','',self.to)).get()
            return page.visible
        except:
            return True
    