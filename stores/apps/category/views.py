import datetime, logging

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from auctions.forms import AuctionSessionForm
from auctions.models import AuctionSession 
from core.decorators import shop_admin_required

from market.forms import MarketCategoryForm, MarketSubCategoryForm
from market.models import MarketCategory, MarketSubCategory


@shop_admin_required
def ajax_category_add(request):
    return HttpResponse(400)
    form_category = MarketCategoryForm(request.POST or None, prefix="category")
    if form_category.is_valid():
        category = form_category.save(commit=False)
        category.shop = request.shop
        category.save()
        return HttpResponse("")
    return render_to_response('category/ajax_category_add.html', {'form_category': form_category},
                              RequestContext(request))


@shop_admin_required
def ajax_category(request):
    marketplace = request.shop.marketplace
    categories = MarketCategory.objects.filter(marketplace=marketplace)
    html = ""
    for cat in categories:
        html += '<option value="%d">%s</option>' % (cat.id, cat.name)
    return HttpResponse(html)


@shop_admin_required
def ajax_sub_category_add(request):
    return HttpResponse(400)
    form_sub_category = MarketSubCategoryForm(request, request.POST or None, prefix="sub_category")
    if form_sub_category.is_valid():
        subcategory = form_sub_category.save(commit=False)
        subcategory.shop = request.shop
        subcategory.save()
        return HttpResponse("")
    return render_to_response('category/ajax_sub_category_add.html', {'form_sub_category': form_sub_category},
                              RequestContext(request))


@shop_admin_required
def ajax_sub_category(request):
    categories = request.POST.getlist('categories[]')
    logging.info("%s" % categories)
    sub_categories = MarketSubCategory.objects.filter(parent__in=categories)
    html = ""
    for sub in sub_categories:
        html += '<option value="%d">%s</option>' % (sub.id, sub.name)
    logging.error(html)
    return HttpResponse(html)


@shop_admin_required
def ajax_session_add(request):
    try:
        form_session = AuctionSessionForm(request.POST or None, prefix="session")
        if form_session.is_valid():
            today = datetime.datetime.today()
            
            sessions = AuctionSession.objects.filter(shop=request.shop).filter(end__gt=today)
            html = ""
            for session in sessions:
                html += '<option value="%d">%s</option>' % (session.id, session.title)
                
            auction_session = form_session.save(commit = False)
            d = datetime.datetime(form_session.cleaned_data['date_from'].year,
                                  form_session.cleaned_data['date_from'].month,
                                  form_session.cleaned_data['date_from'].day,
                                  #int(form_session.cleaned_data['hour_from']),
                                  #int(form_session.cleaned_data['minute_from']))
                                  )
            auction_session.start = d 
            d = datetime.datetime(form_session.cleaned_data['date_to'].year,
                                  form_session.cleaned_data['date_to'].month,
                                  form_session.cleaned_data['date_to'].day,
                                  #int(form_session.cleaned_data['hour_to']),
                                  #int(form_session.cleaned_data['minute_to']))
                                  )
            auction_session.end = d
            auction_session.shop = request.shop
            auction_session.save() 
            
            html += '<option value="%d" selected="selected">%s</option>' % (auction_session.id, auction_session.title)    
            return HttpResponse(html)
        
        return render_to_response('category/ajax_session_add.html', {'form_session': form_session},
                                  RequestContext(request))
    except:
        import logging
        logging.exception("MUERE")


@shop_admin_required
def ajax_session(request):
    today = datetime.datetime.today()
    
    sessions = AuctionSession.objects.filter(shop=request.shop).filter(end__gt=today)
    html = ""
    for session in sessions:
        html += '<option value="%d">%s</option>' % (session.id, session.title)
    
    return HttpResponse(html)      
