from django.db import models
from django.template.defaultfilters import slugify

from market.models import MarketPlace
from core.thumbs import ImageWithThumbsField
from blog_pages.models import Post

class MarketPlaceAnnouncement(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    posted_on = models.DateTimeField(auto_now_add=True)
    posted_by = models.CharField(max_length=100)
    announcement = models.TextField()
    #image = models.ImageField(upload_to='img/announcement')
    image = ImageWithThumbsField(upload_to='img/announcement', sizes=((100,100),))
    def __str__(self):
        return "%s > %s - %s" % (self.marketplace, self.posted_on, self.posted_by)
    
    
class FAQCategory(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    posted_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    #image = models.ImageField(upload_to='img/faq')
    image = ImageWithThumbsField(upload_to='img/faq', sizes=((100,100),), blank=True)
    order = models.IntegerField(default=5)
    def __str__(self):
        return "%s :: %s" % (self.marketplace, self.name)
    
    
class FAQEntry(models.Model):
    category = models.ForeignKey(FAQCategory)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    anchor = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=5)
    def __str__(self):
        return "%s > %s" % (self.category, self.question)
    
    def save(self, *args, **kwargs):
        self.anchor = slugify(self.question)
        super(FAQEntry, self).save(*args, **kwargs)
        
class PostEditorPick(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    order = models.IntegerField(default=5)
    post = models.ForeignKey(Post)
    def __str__(self):
        return "%s > %s (%s)" % (self.marketplace, self.post, self.order)
