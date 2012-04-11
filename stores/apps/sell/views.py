import datetime

from django.db.models import Sum
from django.core.urlresolvers import reverse
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auctions.forms import AuctionSessionForm
from auctions.models import AuctionSession 
from auth.models import User
from core.decorators import shop_admin_required

from models import Payment, Shipping, Sell


from datetime import timedelta

PAGE_SELL = 5


@shop_admin_required
def sell_all(request):
    shop = request.shop
    
    sell_list = Sell.objects.filter(shop=shop).order_by("-date_time")

    pager = Paginator(sell_list, PAGE_SELL)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        sells = pager.page(page)
    except (EmptyPage, InvalidPage):
        sells = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response('sell/sell_all.html', 
                              {'sells': sells,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request))    

@shop_admin_required
def sell_details(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    
    if sell.shop != shop:
        raise Http404
    return render_to_response('sell/sell_details.html', 
                              {'sell': sell},
                              RequestContext(request))

@shop_admin_required
def sell_manual_pay(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    sell.payment.pay()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 


@shop_admin_required
def sell_manual_fail(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    sell.payment.fail()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 

@shop_admin_required
def sell_dispatched(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    
    if sell.shop != shop:
        raise Http404
    sell.shipping.dispatched()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id]))

@shop_admin_required
def sel_undispatched(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    
    if sell.shop != shop:
        raise Http404
    sell.shipping.undispatched()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id]))

@shop_admin_required
def sell_fulfilled(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    
    if sell.shop != shop:
        raise Http404
    sell.shipping.fulfilled()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id]))    


@shop_admin_required
def sell_close(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    sell.close()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 


@shop_admin_required
def sell_open(request, id):
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    sell.open()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 

@shop_admin_required
def sell_cancel(request, id):
    from models import SellError
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    try:
        sell.cancel_sell()
        request.flash['message'] = unicode(_("Operation successfully saved."))
        request.flash['severity'] = "success"
    except SellError, e:
        request.flash['message'] = e 
        request.flash['severity'] = "error"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 

@shop_admin_required
def sell_refund(request, id):
    from models import SellError
    sell = get_object_or_404(Sell, pk=id)
    shop = request.shop
    if sell.shop != shop:
        raise Http404
    try:
        sell.refund()
        request.flash['message'] = unicode(_("Operation successfully saved."))
        request.flash['severity'] = "success"
    except SellError, e:
        request.flash['message'] = e 
        request.flash['severity'] = "error"
    return HttpResponseRedirect(reverse('sell_details', args=[id])) 
