import random
import logging
import twitter
from auth.models import User
from bitlyapi import bitly

from django.core.urlresolvers import reverse
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import slugify
from core.thumbs import ImageWithThumbsField
from django.conf import settings

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

class MarketPlaceSettings(models.Model):
    marketplace = models.OneToOneField(MarketPlace)
    
    twitter_maxlength = models.IntegerField(null=True, blank=True, default=140, help_text="Max number of characters in a tweet")
    twitter_consumer_key = models.CharField(null=True, blank=True, max_length=255)
    twitter_consumer_secret = models.CharField(null=True, blank=True, max_length=255, help_text="Remember this should not be shared")
    twitter_access_token = models.CharField(null=True, blank=True, max_length=255)
    twitter_access_token_secret = models.CharField(null=True, blank=True, max_length=255, help_text="Remember this should not be shared")
    
    def __unicode__(self):
        return u'%s extra settings' % self.marketplace.name


def build_image_item_filename(instance, filename):
    import uuid
    return "images/%s-%s" % (uuid.uuid4(), filename)

class MarketCategory(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60, unique=True)
    order = models.IntegerField(default=255)
    image = ImageWithThumbsField(upload_to=build_image_item_filename, sizes=((100,100),(400,400)), crop=False, null=True, blank=True)
    
    def related_shops(self):
        from django.db.models import Count
        from inventory.models import Product
        from shops.models import Shop

        related_shops = []
        for product in Product.objects.filter(category=self).values('category','shop').annotate(number_products=Count('category')).order_by('-number_products'):
#            related_shops.append((Shop.objects.get(id=product['shop']), product['number_products']))
            related_shops.append(Shop.objects.get(id=product['shop']))

        return related_shops
    
    @classmethod
    def generate_captcha(cls):
        index = random.randint(0, cls.objects.count() - 1)
        captcha = cls.objects.all()[index].name.split()[0]
        return captcha, captcha

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
    image = ImageWithThumbsField(upload_to=build_image_item_filename, sizes=((100,100),(400,400)), crop=False, null=True, blank=True)
    
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
    post_to_twitter = models.BooleanField(default=True)
    
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
    
    def get_absolute_url(self):
        return u'http://%s%s' %(self.marketplace.base_domain, reverse('market_blog_view_post', args=[self.slug]))
    
    def tweet_text(self):
        try:
            api = bitly.BitLy(api_user=settings.BITLY_USERNAME, api_key=settings.BITLY_API_KEY)
            res = api.shorten(longUrl=self.get_absolute_url())
            link = res['url']
        except Exception, ex:
            logging.error(str(ex))
            link = self.get_absolute_url()

        mesg = u'%s - %s' % (self.title, link)

        TWITTER_MAXLENGTH = self.marketplace.marketplacesettings.twitter_maxlength
        if len(mesg) > TWITTER_MAXLENGTH:
            size = len(mesg + '...') - TWITTER_MAXLENGTH
            mesg = u'%s... - %s' % (self.title[:-size], link)

        return mesg
    
    def tweet(self):
        try:
            CONSUMER_KEY        = self.marketplace.marketplacesettings.twitter_consumer_key
            CONSUMER_SECRET     = self.marketplace.marketplacesettings.twitter_consumer_secret
            ACCESS_TOKEN        = self.marketplace.marketplacesettings.twitter_access_token
            ACCESS_TOKEN_SECRET = self.marketplace.marketplacesettings.twitter_access_token_secret

            api = twitter.Api(consumer_key=CONSUMER_KEY,
                              consumer_secret=CONSUMER_SECRET,
                              access_token_key=ACCESS_TOKEN,
                              access_token_secret=ACCESS_TOKEN_SECRET)

            api.PostUpdate(self.tweet_text())
        except Exception, e:
            logging.error(str(e))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        
        if self.post_to_twitter:
            self.tweet()

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

class ContactFormInfo(models.Model):
    marketplace = models.ForeignKey(MarketPlace)
    datetime = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=64, null=True)
    ip = models.CharField(max_length=64)

    def __unicode__(self):
        return u'Contact Form at %s %s %s' %(self.datetime, self.email, self.ip)
