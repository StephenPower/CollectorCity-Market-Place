import logging


from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
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

@shop_admin_required 
def shop_billing(request):
    shop = request.shop
    credit_card = shop.billing_info().credit_card()
    return render_to_response('store_admin/account/billing_overview.html', {'credit_card' : credit_card}, 
                              RequestContext(request))

@shop_admin_required
def shop_billing_update_credit_card(request):
    from django.conf import settings
    from store_admin.forms import CreditCardForm
    from payments.gateways.braintreegw import BraintreeGateway
    
    shop = request.shop
    form = CreditCardForm(request.POST or None)
    error_message = None
    if request.method == "POST":
        if form.is_valid():
            gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
            
            customer_id = shop.billing_info().customer_id
            cc_cardholder = form.cleaned_data['card_holder_name']
            cc_number = form.cleaned_data['card_number']
            cc_expiration_date = form.cleaned_data['expiration_date']
            cc_security_number = form.cleaned_data['security_number']
            result = gw.new_customer_credit_card(customer_id, cc_cardholder, cc_number, cc_expiration_date, cc_security_number)
            
            if result.is_success:
                request.flash['message'] = "Your credit card information was successfully updated!"
                request.flash['severity'] = "success"
                return HttpResponseRedirect(reverse("billing_overview"))  
            else:
                error_message = result.message or "No error message available"
                
    params = {'form': form, 'error_message': error_message}
    return render_to_response('store_admin/account/billing_update_credit_card.html', params, RequestContext(request))

@shop_admin_required
def shop_purchases(request):
    from subscriptions.models import FeaturePayment
    
    shop = request.shop
    
    purchases = FeaturePayment.objects.filter(shop=shop).order_by("-timestamp")
    
    return render_to_response('store_admin/account/purchases_overview.html', {'purchases':purchases}, RequestContext(request))