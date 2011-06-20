import logging


from django.http import HttpResponse
from subscriptions.models import SubscriptionPlan
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from core.decorators import shop_admin_required


def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(active=True).filter(visible=True)   
    return render_to_response("shops/pricing.html", {'plans' : plans}, RequestContext(request))

@shop_admin_required 
def shop_subscription_overview(request):
    from subscriptions.models import Subscription
    
    shop = request.shop
    profile = shop.admin.get_profile()
    try:
        subscription = Subscription.objects.filter(owner=profile).get()
    except Subscription.DoesNotExist:
        subscription = None
    
    return render_to_response('store_admin/account/subscription_overview.html', {'subscription' : subscription}, 
                              RequestContext(request))


@shop_admin_required 
def shop_subscription_plans(request):
    from subscriptions.models import SubscriptionPlan
    plans = SubscriptionPlan.objects.filter(active=True).filter(visible=True)
    
    return render_to_response('store_admin/account/subscription_plans.html', {'plans': plans}, 
                              RequestContext(request))
