# Create your views here.
import datetime
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from auth.decorators import login_required
from django.http import HttpResponseRedirect
from shops.models import Shop, ShopBillingInfo 
from subscriptions.models import Subscription, SubscriptionPlan

from market_sell.forms import ShopSignUpWizard, ShopInfoForm, ShopPlanForm, ShopBillingForm
   
@transaction.commit_on_success
@login_required
def signup(request, plan="None"):
    init = {0: {}, 1:{}, 2:{}}
    user = request.user
    if user.shop_set.count() > 0:
        request.flash['message'] = unicode(_("You already have a store! Only one shop per user is allowed."))
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse("market_home"))
              
    return ShopSignUpWizard([ShopInfoForm, ShopPlanForm, ShopBillingForm], initial=init)(request) 

def welcome(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    profile = shop.admin.get_profile()
    try:
        shopinfo = ShopBillingInfo.objects.filter(shop=profile).get()

    except ShopBillingInfo.DoesNotExist:
        shopinfo = None

    try:
        subscription = Subscription.objects.filter(owner=profile).get()

    except Subscription.DoesNotExist:
        subscription = None

    return render_to_response("%s/sell/welcome.html" % request.marketplace.template_prefix, 
                              {'shop': shop, 'subscription': subscription, 'shopinfo': shopinfo},
                              RequestContext(request))
    
def privacy_policy(request):
    
    return render_to_response("%s/sell/privacy.html" % request.marketplace.template_prefix, 
                              {},
                              RequestContext(request))
def plans(request):
    marketplace= request.marketplace
    try:
        marketplans = SubscriptionPlan.objects.filter(marketplace=marketplace).filter(active="True").filter(visible=True).order_by('-price')

    except SubscriptionPlan.DoesNotExist:
        marketplans = None

    return render_to_response("%s/sell/plans.html" % request.marketplace.template_prefix, 
                              {'marketplans': marketplans},
                              RequestContext(request))

def features(request):
    marketplace= request.marketplace
    try:
        marketplans = SubscriptionPlan.objects.filter(marketplace=marketplace).filter(active="True").filter(visible=True).order_by('-price')
    except SubscriptionPlan.DoesNotExist:
        marketplans = None

    return render_to_response("%s/sell/features.html" % request.marketplace.template_prefix, 
                              {'marketplans': marketplans},
                              RequestContext(request))
