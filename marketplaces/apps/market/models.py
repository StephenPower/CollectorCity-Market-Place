from auth.models import User

from django.contrib import admin
from django.db import models
from django.template.defaultfilters import slugify

class MarketPlace(models.Model):
    #length  
    name = models.CharField(max_length=92)
    slug = models.SlugField(max_length=92, unique=True)
    title = models.CharField(max_length=92)
    base_domain =  models.CharField(max_length=128, help_text="example: greatcoins.com", unique=True)
    contact_email = models.EmailField(help_text="This email will be shown in the contact us page", default="contact@yourstore.com")
    contact_phone = models.CharField(max_length=128, help_text="This phone will be shown in the contact us page", default="")
    charge_on_card_as = models.CharField(max_length=255, help_text="Collector City LLC", default="")
    template_prefix = models.SlugField(max_length=92, help_text="example: greatcoins", unique=True)
    
    def __unicode__(self):
        return self.name
    
    def privacy_policy(self):
        policies = self.privacypolicy_set.all()
        l = policies.count()
        if l > 0: return policies[l-1].text
   
class MarketCategory(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60, unique=True)
    order = models.IntegerField(default=255)
    
    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return "%s > %s" % (self.marketplace, self.name)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(MarketCategory, self).save(*args, **kwargs)

class MarketSubCategory(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60)
    parent = models.ForeignKey(MarketCategory, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=255)
    
    class Meta:
        unique_together = (('parent', 'slug'),)
        ordering = ['order']
    
    def __unicode__(self):
        return "%s > %s" % (self.parent, self.name)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(MarketSubCategory, self).save(*args, **kwargs)

class MarketMailingListMember(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    email = models.EmailField()
    def __str__(self):
        return "%s > %s" % (self.marketplace, self.email)
    
class MarketPostCategory(models.Model):
    tag = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    def __unicode__(self):
        return self.tag
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super(MarketPostCategory, self).save(*args, **kwargs)

class MarketBlogPost(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    title = models.CharField(max_length=60)
    body = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User)
    views = models.IntegerField(default=0, editable=False)
    allow_comments = models.BooleanField(default=False)
    slug = models.SlugField(max_length=80, unique=True, editable=False)
    #tags = models.
    
    class Admin:
        list_display   = ('title', 'posted_by', 'posted_on')
        list_filter    = ('publisher', 'publication_date')
        ordering       = ('-posted_on',)
        search_fields  = ('title', 'posted_on')

    def comments(self):
        comment_list = MarketPostComment.objects.filter(post=self).order_by("-commented_on")
        return comment_list
        
    def tags(self):
        return []
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(MarketBlogPost, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return "%s > %s" % (self.marketplace, self.title)
    
    def visited(self):
        self.views = self.views + 1
        self.save()
        
    def date(self):
        return self.posted_on.strftime("%B %d, %Y")

class MarketPostPick(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    post = models.ForeignKey(MarketBlogPost)
    order = models.IntegerField(default=5)


class MarketPostComment(models.Model):
    post = models.ForeignKey(MarketBlogPost)
    comment = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    def date(self):
        return self.commented_on.strftime("%B %d, %Y")

class PrivacyPolicy(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    text = models.TextField(default="")
    
    def __unicode__(self):
        return "%s > Privacy Policy" % self.marketplace
    
class TermsAndConditions(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    text = models.TextField(default="")
    
    def __unicode__(self):
        return "%s > Terms & Conditions" % self.marketplace