# Create your views here.
import datetime
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from auth.models import User
from auth.decorators import login_required
from django.http import HttpResponseRedirect
from shops.models import Shop, ShopBillingInfo 
 

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
    return render_to_response("%s/sell/welcome.html" % request.marketplace.template_prefix, 
                              {'shop': shop },
                              RequestContext(request))
    
def privacy_policy(request):
    
    return render_to_response("%s/sell/privacy.html" % request.marketplace.template_prefix, 
                              {},
                              RequestContext(request))