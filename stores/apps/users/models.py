from django.db import models

from auth.models import User
from sell.models import Payment, Sell, Cart
from core.thumbs import ImageWithThumbsField

class Profile(models.Model):
    user = models.OneToOneField(User)
    street_address = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    state = models.CharField(max_length=80, blank=True, null=True)
    zip = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    birth = models.DateField(blank=True, null=True)
    photo = ImageWithThumbsField(upload_to='images', sizes=((100,100),((128,135)),(400,400)))
    #photo = models.ImageField(upload_to='images', blank=True, null=True)
    
    def get_cart(self, shop):
        try:
            cart = Cart.objects.filter(shop=shop).filter(bidder=self.user).get()
        except Cart.DoesNotExist:
            raise Exception("Profile %s don't have a Cart associated yet!" % self)
        return cart

    def get_sell(self):
        try:
            payment = Payment.objects.filter(sell__bidder=self.user, state_actual__state='PE').get()
            return payment.sell
        except Payment.DoesNotExist:
            return Sell.new_sell(self.shop, self.user)

    def set_subscription_plan(self, plan_id, subscription_id):
        from subscriptions.models import Subscription, SubscriptionPlan
        
        subscription_plan = SubscriptionPlan.objects.filter(plan_id=plan_id).get()
        subscription = Subscription(owner=self, subscription_id=subscription_id, plan=subscription_plan)
        subscription.save()
    
    
    def __unicode__(self):
        return "Profile<%s>" % (self.user.username)

class EmailVerify(models.Model):
    user = models.OneToOneField(User)
    date = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=50)
    mail = models.EmailField()
    user_activation = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    
    def generate_code(self):
        """
           Generate a random code for validation 
        """
        import uuid
        
        while True:
            code = str(uuid.uuid4())
            try:
                EmailVerify.objects.filter("code =", code).get()
            except:
                self.code = code
                break
        self.save()
        return self.code