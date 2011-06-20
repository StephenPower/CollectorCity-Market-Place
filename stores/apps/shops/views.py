import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.db import transaction

from django.utils.translation import ugettext as _

from core.decorators import superuser_required
from core.decorators import shop_admin_required

from blog_pages.models import Home, About, Menu 

from auth.models import User
from users.models import Profile
from preferences.models import DnsShop, Preference
from payments.gateways.braintreegw import BraintreeGateway
from subscriptions.models import Subscription, SubscriptionPlan, SubscriptionCancelation
    
from forms import ShopForm
from models import Shop


@superuser_required
def shop_list(request):
    
    shops = Shop.objects.all()
    return render_to_response('shops/shop_list.html', {'shops': shops}, 
                              RequestContext(request))

@superuser_required
def shop_subscription(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    profile = shop.admin.get_profile()
    try:
        subscription = Subscription.objects.filter(owner=profile).get()
        
    except Subscription.DoesNotExist:
        subscription = None
    
    return render_to_response('shops/shop_subscription.html', {'shop' : shop, 'subscription' : subscription}, 
                              RequestContext(request))

def change_subscription_plan(request, plan_id):
    
    plan_id = long(plan_id)
    shop = request.shop
    new_plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    logging.debug("New Plan >> %s" % new_plan)
    
    shop_subscription = Subscription.objects.filter(owner=shop.admin.get_profile()).get()
    logging.debug("Current Plan >> %s" % shop_subscription.plan)
    
    if shop_subscription.plan.id != plan_id:
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        result = gw.change_subscription(shop_subscription.subscription_id, new_plan.plan_id)
        if result.is_success:
            shop_subscription.plan = new_plan
            shop_subscription.save()
            
            request.flash['message'] = _("Congratulations!! You have successfully changed your subscription plan to %s!" % new_plan.name)
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('subscription_plans'))
        else:
            logging.error(result.message)
            request.flash['message'] = _("There was an error when trying to upgrade/downgrade your subscription plan!")
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('subscription_plans'))
    else:
        request.flash['message'] = _("You are already subscribed to this plan!")
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('subscription_plans'))
    
@shop_admin_required
def shop_cancel_subscription(request, shop_id):
    from subscriptions.models import Subscription
    shop = get_object_or_404(Shop, pk=shop_id)
    profile = shop.admin.get_profile()
    try:
        subscription = Subscription.objects.filter(owner=profile).get()
                 
        gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        result = gw.cancel_subscription(subscription.subscription_id)
        
        if result.is_success:
            subscription.status = 'C'
            subscription.save()
            
            subscription_cancelation = SubscriptionCancelation(shop=shop, subscription=subscription)
            subscription_cancelation.save()
            
            request.flash['message'] = _("Subscription Cancelled")
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('subscription_overview'))
        
        request.flash['message'] = _("Subscription could not be cancelled. %s" % result.message)
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('subscription_overview'))
        
    except Subscription.DoesNotExist:
        request.flash['message'] = _("Subscription not found!")
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('subscription_overview'))
    

def welcome_shop(request, id):
    shop = get_object_or_404(Shop, pk=id)
    return render_to_response('shops/welcome_shop.html', {'shop': shop}, RequestContext(request))
