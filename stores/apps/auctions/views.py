from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from forms import AuctionSessionForm
from models import AuctionSession

from core.decorators import shop_admin_required

import datetime

PAGE_AUCTIONS = 10

#@shop_admin_required    
#def auctions_list(request):
#    shop = request.shop
#    filter_by = request.GET.get('filter_by','')
#    order_by = request.GET.get('order_by','')
#    filter_params = {'order_by':order_by,
#                     'filter_by':filter_by,}
#    q_title=''
#        
#    all_auctions = AuctionSession.objects.all().filter(shop=shop)
#
#    if filter_by == 'title':
#        q_title = request.GET.get('q_title','')
#        all_auctions = all_auctions.filter(title__icontains=q_title)
#        
#    elif filter_by == 'finished':
#        all_auctions = all_auctions.filter(end__lt=datetime.datetime.now())
#    elif filter_by == 'actual':
#        all_auctions = all_auctions.filter(end__gt=datetime.datetime.now(), start__lt=datetime.datetime.now())
#    elif filter_by == 'future':
#        all_auctions = all_auctions.filter(start__gt=datetime.datetime.now())
#
#
#    if order_by == 'id':
#        all_auctions = all_auctions.order_by("id")
#    elif order_by == '-id':
#        all_auctions = all_auctions.order_by("-id")
#    elif order_by == 'title':
#        all_auctions = all_auctions.order_by("title")
#    elif order_by == '-title':
#        all_auctions = all_auctions.order_by("-title")
#    elif order_by == 'start':
#        all_auctions = all_auctions.order_by("start")
#    elif order_by == '-start':
#        all_auctions = all_auctions.order_by("-start")
#    elif order_by == 'end':
#        all_auctions = all_auctions.order_by("end")
#    elif order_by == '-end':
#        all_auctions = all_auctions.order_by("-end")
#    elif order_by == 'total':
#        all_auctions = all_auctions.order_by("lot_set__count")
#    elif order_by == '-total':
#        all_auctions = all_auctions.order_by("-lot_set__count")
#    
#
#    pager = Paginator(all_auctions, PAGE_AUCTIONS)
#    try:
#        page = int(request.GET.get('page','1'))
#    except:
#        page = 1
#    try:
#        auctions = pager.page(page)
#    except (EmptyPage, InvalidPage):
#        auctions = pager.page(pager.num_pages)
#    paged = (pager.num_pages > 1)
#         
#    return render_to_response('auctions/auctions_list.html', 
#                              {'auctions': auctions,
#                               'pages': pager.page_range,
#                               'paged': paged,
#                               'filter_params': filter_params,
#                               'q_title': q_title,
#                              }, 
#                              RequestContext(request))



    

@shop_admin_required    
def auction_add(request):
    form = AuctionSessionForm(request.POST or None)
    if form.is_valid():
        auction_session = form.save(commit = False)
        d = datetime.datetime(form.cleaned_data['date_from'].year,
                              form.cleaned_data['date_from'].month,
                              form.cleaned_data['date_from'].day,
                              form.cleaned_data['time_from'].hour,
                              form.cleaned_data['time_from'].minute)
        auction_session.start = d 
        d = datetime.datetime(form.cleaned_data['date_to'].year,
                              form.cleaned_data['date_to'].month,
                              form.cleaned_data['date_to'].day,
                              form.cleaned_data['time_to'].hour,
                              form.cleaned_data['time_to'].minute)
        auction_session.end = d
        auction_session.shop = request.shop
        auction_session.save() 
        request.flash['message'] = unicode(_("Session successfully added."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('inventory_auctions'))
    return render_to_response('auctions/auction_add.html', 
                              {'form': form},
                              RequestContext(request))



def auction_details(request, auction_id):
    auction = get_object_or_404(AuctionSession, pk=auction_id)
    shop = request.shop
    if auction.shop != shop:
        raise Http404
    return render_to_response('auctions/auction_details.html', 
                              {'auction': auction}, 
                              RequestContext(request))
