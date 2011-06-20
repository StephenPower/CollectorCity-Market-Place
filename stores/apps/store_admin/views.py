import logging
import datetime
import urllib

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auctions.models import AuctionSession
from for_sale.models import Item
from core.decorators import shop_admin_required

from market.models import MarketCategory, MarketSubCategory

PAGE_ITEMS = 10

@shop_admin_required
def back_to_site(request):
    request.session['admin_checkpoint'] = request.META.get('HTTP_REFERER', '/admin')
    shop_checkpoint = request.session.get("shop_checkpoint", "/") 
    return HttpResponseRedirect(shop_checkpoint)


@shop_admin_required
def redirect_admin(request):
    request.session['shop_checkpoint'] = request.META.get('HTTP_REFERER', '/')
    admin_checkpoint = request.session.get("admin_checkpoint", "/admin") 
    return HttpResponseRedirect(admin_checkpoint)

@shop_admin_required
def home_admin(request):
    return render_to_response('store_admin/home_admin.html', {}, RequestContext(request)) 
    
    
@shop_admin_required
def customers_overview(request):
    from sell.models import Sell
    from market_buy.models import WishListItem
    marketplace = request.shop.marketplace
    
    sells = Sell.objects.filter(shop=request.shop, closed=False).order_by("-date_time")[:5]
    wishlistitems = WishListItem.objects.filter(marketplace=marketplace)
    
    return render_to_response('store_admin/customers/overview.html',
                               {
                                'sells': sells,
                                'wishlistitems' : wishlistitems,
                               }
                               , RequestContext(request))


@shop_admin_required
def customers_profiles(request):
    return render_to_response('store_admin/customers/profiles.html', {}, 
                              RequestContext(request))


@shop_admin_required
def customers_sold_items(request):
    from sell.models import Sell

    filter_by = request.GET.get('filter_by','')
    order_by = request.GET.get('order_by','')
    show = request.GET.get('show','')
    filter_params = {'order_by':order_by,
                     'filter_by':filter_by,
                     'show':show,}
    q_user=''
    
    shop = request.shop
    
    sell_list = Sell.objects.filter(shop=shop)
    
    if filter_by == 'for_date_today':
        d = datetime.datetime.now()
        date_from = datetime.datetime(d.year, d.month, d.day)
        date_to = date_from + datetime.timedelta(1)
        sell_list = sell_list.filter(date_time__range=(date_from, date_to))
    elif filter_by == 'for_date_week':
        d = datetime.datetime.now()
        delta = d.weekday()
        date_from = d - datetime.timedelta(delta)        
        sell_list = sell_list.filter(date_time__range=(date_from, d))
    elif filter_by == 'for_date_month':
        sell_list = sell_list.filter(date_time__month=datetime.datetime.now().date().month)
    elif filter_by == 'for_date_year':
        sell_list = sell_list.filter(date_time__year=datetime.datetime.now().date().year)

    elif filter_by == 'payment_pending':
        sell_list = sell_list.filter(payment__state_actual__state='PE')
    elif filter_by == 'payment_paid':
        sell_list = sell_list.filter(payment__state_actual__state='PA')
    elif filter_by == 'payment_failed':
        sell_list = sell_list.filter(payment__state_actual__state='FA')

    elif filter_by == 'shipping_pending':
        sell_list = sell_list.filter(shipping__state_actual__state='PE')
    elif filter_by == 'shipping_dispatched':
        sell_list = sell_list.filter(shipping__state_actual__state='DI')
    elif filter_by == 'shipping_fullfilled':
        sell_list = sell_list.filter(shipping__state_actual__state='FU')

    elif filter_by == 'user':
        q_user = request.GET.get('q_user','')
        f = Q(bidder__username__icontains=q_user)|Q(bidder__first_name__icontains=q_user)|Q(bidder__last_name__icontains=q_user)
        sell_list = sell_list.filter(f)

    if show == 'open':
        sell_list = sell_list.filter(closed=False)
    elif show == 'close':
        sell_list = sell_list.filter(closed=True)
    else:
        sell_list = sell_list.filter(closed=False)

    if order_by == 'oldest':
        sell_list = sell_list.order_by("id")
    elif order_by == 'newest':
        sell_list = sell_list.order_by("-id")
    elif order_by == 'username':
        sell_list = sell_list.order_by("bidder__username")
    elif order_by == '-username':
        sell_list = sell_list.order_by("-bidder__username")
    elif order_by == 'total':
        sell_list = sell_list.order_by("total")
    elif order_by == '-total':
        sell_list = sell_list.order_by("-total")
    else:
        sell_list = sell_list.order_by("-date_time")


        
    pager = Paginator(sell_list, 5)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        sells = pager.page(page)
    except (EmptyPage, InvalidPage):
        sells = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    params = {
        'sells': sells,
        'pages': pager.page_range,
        'paged': paged,
        'filter_params': filter_params,
        'q_user': q_user,
    }
    
    return render_to_response('store_admin/customers/sold_items.html', params, RequestContext(request))


@shop_admin_required
def customers_payments(request):
    return render_to_response('store_admin/customers/payments.html', {}, 
                              RequestContext(request))


@shop_admin_required
def customers_shipments(request):
    return render_to_response('store_admin/customers/shipments.html', {}, 
                              RequestContext(request))


@shop_admin_required
def customers_wish_lists(request):
    from market_buy.models import WishListItem
    
    marketplace = request.shop.marketplace
    wishlistitems = WishListItem.objects.filter(marketplace=marketplace)
    
    search_text = ''
    if request.method == "POST":
        search_text = request.POST.get("search_text")
        wishlistitems = wishlistitems.filter(description__contains=search_text)
    
    else:
        sort = request.GET.get('sort_by', 'oldest')
        if sort == "oldest": wishlistitems = wishlistitems.order_by("id")
        if sort == "newest": wishlistitems = wishlistitems.order_by("-id")
        if sort == "category": wishlistitems = wishlistitems.order_by("category__name")
        if sort == "username": wishlistitems = wishlistitems.order_by("posted_by__username")
        if sort == "price": wishlistitems = wishlistitems.order_by("ideal_price")
        if sort == "-price": wishlistitems = wishlistitems.order_by("-ideal_price")
    
    return render_to_response('store_admin/customers/wish_lists.html', 
                              {
                               'wishlistitems' : wishlistitems,
                               'search_text': search_text,
                               }, 
                              RequestContext(request))

@shop_admin_required
def customers_send_notification(request, id):
    from market_buy.models import WishListItem
    from django.core.mail import send_mail
    
    wishitem = get_object_or_404(WishListItem, pk=id)
    
    shop = request.shop
    
    subject = "Notification from %s" % shop.name_shop()
    the_wish = "Hi %s, you have post an item in the wish list of %s on %s. You have specified the following information about your wish item: \n\n- Description: %s\n- Ideal Price: $%s\n- Category: %s\n- Subcategory: %s" % (wishitem.posted_by.get_full_name() or wishitem.posted_by.username , wishitem.marketplace, wishitem.posted_on, wishitem.description, wishitem.ideal_price, wishitem.category.name, wishitem.subcategory.name)
    the_message = "%s from %s has found an item that appears to match the item you are looking for. Contact %s at %s" % (shop.admin.get_full_name() or shop.admin.username, shop.name_shop(), shop.admin, shop.default_dns)
    body = the_wish + "\n\n" + the_message
    to = wishitem.posted_by.email
    
    send_mail(subject, body, shop.admin.email, [to], fail_silently=True)
    request.flash['message'] = "Notification sent..."
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse("customers_wish_lists"))
@shop_admin_required
def customers_mailing_list(request):
    from shops.models import MailingListMember
    
    shop = request.shop
    mailing_list = MailingListMember.objects.filter(shop=shop)
    
    search_text = ''
    if request.method == "POST":
        search_text = request.POST.get("search_text")
        mailing_list = mailing_list.filter(email__contains=search_text)
    
    else:    
        sort = request.GET.get('sort_by', 'oldest')
        if sort == "email": mailing_list = mailing_list.order_by("email") 
        if sort == "-email": mailing_list = mailing_list.order_by("-email")
        if sort == "oldest": mailing_list = mailing_list.order_by("id")
        if sort == "newest": mailing_list = mailing_list.order_by("-id")
        
    return render_to_response('store_admin/customers/mailing_list.html', 
                              {
                               'mailing_list' : mailing_list,
                               'search_text': search_text,
                               }, 
                              RequestContext(request))   

@shop_admin_required
def customers_export_mailinglist(request):
    import csv
    
    shop = request.shop
    
    # Create the HttpResponse object with the appropriate CSV header.
    filename = "%s_%s" % (shop.default_dns, 'mailing_list.csv')
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    writer = csv.writer(response)
    
    for member in shop.mailinglistmember_set.all():
        writer.writerow([member.email])
    
    return response

    
@shop_admin_required
def web_store_overview(request):
    from blog_pages.models import Page, Post, DynamicPageContent
    
    shop = request.shop    
    static_pages = Page.objects.filter(shop = shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop = shop)
    posts = Post.objects.filter(shop = shop)
    return render_to_response('store_admin/web_store/overview.html', 
                              {'static_pages': static_pages, 'dynamic_pages': dynamic_pages, 'posts': posts},
                              RequestContext(request))


@shop_admin_required
def inventory_items_import(request):
    return render_to_response('store_admin/inventory/items_import.html',  {}, RequestContext(request))
    
@shop_admin_required
def inventory_items(request):
    from for_sale.models import Item

    shop = request.shop
    
    
    
    filter_by = request.GET.get('filter_by','')
    order_by = request.GET.get('order_by','')
    q_title = request.GET.get('q_title','')
    id_category = request.GET.get('id_category','')
    id_subcategory = request.GET.get('id_subcategory','')
    
    all_items = Item.objects.all().filter(shop=shop)
    total = all_items.count()
    
    items_per_page = int(request.GET.get('items_per_page', -1))
    if items_per_page == -1:
        if total >= 0 and total <= 10: items_per_page = 10
        elif total > 10 and total <= 50: items_per_page = 20
        elif total > 50 and total <= 100: items_per_page = 50
        else: items_per_page = 100
        
    filter_params = {'order_by':order_by,
                     'filter_by':filter_by,
                     'q_title': q_title,
                     'id_subcategory': id_subcategory,
                     'id_category': id_category,
                     'items_per_page': items_per_page,
                     }
            
    

    if filter_by == 'title':
        q_title = request.GET.get('q_title','')
        all_items = all_items.filter(title__icontains=q_title)
    elif filter_by == 'category':
        id_category = request.GET.get('id_category','')
        category = MarketCategory.objects.get(id=id_category) 
        all_items = all_items.filter(category=category)
    elif filter_by == 'subcategory':
        id_subcategory = request.GET.get('id_subcategory','')
        subcategory = MarketSubCategory.objects.get(id=id_subcategory) 
        all_items = all_items.filter(subcategory=subcategory)

    if order_by == 'oldest':
        all_items = all_items.order_by("id")
    elif order_by == 'newest':
        all_items = all_items.order_by("-id")     
    elif order_by == 'price':
        all_items = all_items.order_by("price")
    elif order_by == '-price':
        all_items = all_items.order_by("-price")
    elif order_by == 'qty':
        all_items = all_items.order_by("qty")
    elif order_by == '-qty':
        all_items = all_items.order_by("-qty")
        

    pager = Paginator(all_items, items_per_page)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        products = pager.page(page)
    except (EmptyPage, InvalidPage):
        products = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)

    
    return render_to_response('store_admin/inventory/items.html', 
                              {'products': products,
                               'total' : total,
                               'pages': pager.page_range,
                               'paged': paged,
                               'filter_params': filter_params,
                               'getvars': '&'+urllib.urlencode(filter_params),
                               'q_title': q_title,
                              }, 
                              RequestContext(request))

@shop_admin_required
def inventory_lots(request):    
    from lots.models import Lot

    shop = request.shop
    
    filter_by = request.GET.get('filter_by','')
    order_by = request.GET.get('order_by','')
    q_title = request.GET.get('q_title','')
    id_category = request.GET.get('id_category','')
    id_subcategory = request.GET.get('id_subcategory','')

    
    all_lots = Lot.objects.all().filter(shop=shop)
    total = all_lots.count()
    
    items_per_page = int(request.GET.get('items_per_page', -1))
    if items_per_page == -1:
        if total >= 0 and total <= 10: items_per_page = 10
        elif total > 10 and total <= 50: items_per_page = 20
        elif total > 50 and total <= 100: items_per_page = 50
        else: items_per_page = 100

    filter_params = {
                     'order_by':order_by,
                     'filter_by':filter_by,
                     'q_title': q_title,
                     'id_subcategory': id_subcategory,
                     'id_category': id_category,
                     'items_per_page': items_per_page,
                     }
        
    if filter_by == 'title':
        q_title = request.GET.get('q_title','')
        all_lots = all_lots.filter(title__icontains=q_title)
    elif filter_by == 'category':
        id_category = request.GET.get('id_category','')
        category = MarketCategory.objects.get(id=id_category) 
        all_lots = all_lots.filter(category=category)
    elif filter_by == 'subcategory':
        id_subcategory = request.GET.get('id_subcategory','')
        subcategory = MarketSubCategory.objects.get(id=id_subcategory) 
        all_lots = all_lots.filter(subcategory=subcategory)
    elif filter_by == 'session':
        id_session = request.GET.get('id_session','')
        session = AuctionSession.objects.get(id=id_session) 
        all_lots = all_lots.filter(session=session)
    elif filter_by == 'active':
        all_lots = all_lots.filter(state='A')
    elif filter_by == 'sold':
        all_lots = all_lots.filter(state='S')
    elif filter_by == 'not_sell':
        all_lots = all_lots.filter(state='N')

    if order_by == 'oldest':
        all_lots = all_lots.order_by("id")
    elif order_by == 'newest':
        all_lots = all_lots.order_by("-id")     
    elif order_by == 'price':
        all_lots = all_lots.order_by("starting_bid")
    elif order_by == '-price':
        all_lots = all_lots.order_by("-starting_bid")
    elif order_by == 'actual_price':
        all_lots = all_lots.order_by("bid_actual__bid_amount")
    elif order_by == '-actual_price':
        all_lots = all_lots.order_by("-bid_actual__bid_amount")
    elif order_by == 'state':
        all_lots = all_lots.order_by("state")
    elif order_by == '-state':
        all_lots = all_lots.order_by("-state")
    

    pager = Paginator(all_lots, PAGE_ITEMS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        products = pager.page(page)
    except (EmptyPage, InvalidPage):
        products = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
         
    return render_to_response('store_admin/inventory/lots.html', 
                              {'products': products,
                               'total': total,
                               'pages': pager.page_range,
                               'paged': paged,
                               'filter_params': filter_params,
                               'getvars': '&'+urllib.urlencode(filter_params),
                               'q_title': q_title,
                              }, 
                              RequestContext(request))
        
@shop_admin_required
def inventory_overview(request):
#    from lots.models import Lot
#    from payments.models import Payment
#    shop = request.shop
#    if request.user.is_superuser:
#        return HttpResponseRedirect(reverse('shop_list'))
#    else:
#        users = []
#        now = datetime.datetime.now().date()
#        
#        lot_revenue_today = Lot.objects.all().filter(shop = shop,
#                                                 state = 'S', 
#                                                 bid_actual__bid_time__year=now.year, 
#                                                 bid_actual__bid_time__month=now.month, 
#                                                 bid_actual__bid_time__day=now.day).aggregate(total=Sum('bid_actual__bid_amount'))
#
#        forsale_revenue_today = Payment.objects.all().filter(shop = shop,
#                                                 state_actual__state='AU',
#                                                 state_actual__date_time__year=now.year,
#                                                 state_actual__date_time__month=now.month,
#                                                 state_actual__date_time__day=now.day).aggregate(total=Sum('total'))
#
#        lot_revenue_today = lot_revenue_today.get('total') or 0
#        forsale_revenue_today = forsale_revenue_today.get('total') or 0 
#        
#        revenue_today = forsale_revenue_today + lot_revenue_today
#                
#        date_from = now - timedelta(now.weekday())
#        date_to = now + timedelta(1)
#        this_week = Lot.objects.all().filter(shop = shop,
#                                             state = 'S', 
#                                             bid_actual__bid_time__range=(date_from, date_to)).aggregate(total=Sum('bid_actual__bid_amount'))
#        this_week = this_week.get('total')
#        if this_week == None: this_week=0 
#        
#        return render_to_response('store_admin/home_admin.html', 
#                                  {'users': users,
#                                   'revenue_today': revenue_today,
#                                   'this_week': this_week,
#                                   }, 
#                                  RequestContext(request))     
    
    return render_to_response('store_admin/inventory/overview.html', {}, 
                              RequestContext(request))

@shop_admin_required
def inventory_auctions(request):
    shop = request.shop
    
    
    filter_by = request.GET.get('filter_by','')
    order_by = request.GET.get('order_by','')
    q_title = request.GET.get('q_title','')
            
    all_auctions = AuctionSession.objects.all().filter(shop=shop)
    total = all_auctions.count()
    
    items_per_page = int(request.GET.get('items_per_page', -1))
    if items_per_page == -1:
        if total >= 0 and total <= 10: items_per_page = 10
        elif total > 10 and total <= 50: items_per_page = 20
        elif total > 50 and total <= 100: items_per_page = 50
        else: items_per_page = 100
        
    filter_params = {
                     'order_by':order_by,
                     'filter_by':filter_by,
                     'items_per_page': items_per_page,
                     }
    
    if filter_by == 'title':
        all_auctions = all_auctions.filter(title__icontains=q_title)
    elif filter_by == 'finished':
        all_auctions = all_auctions.filter(end__lt=datetime.datetime.now())
    elif filter_by == 'actual':
        all_auctions = all_auctions.filter(end__gt=datetime.datetime.now(), start__lt=datetime.datetime.now())
    elif filter_by == 'future':
        all_auctions = all_auctions.filter(start__gt=datetime.datetime.now())


    if order_by == 'id':
        all_auctions = all_auctions.order_by("id")
    elif order_by == '-id':
        all_auctions = all_auctions.order_by("-id")
    elif order_by == 'title':
        all_auctions = all_auctions.order_by("title")
    elif order_by == '-title':
        all_auctions = all_auctions.order_by("-title")
    elif order_by == 'start':
        all_auctions = all_auctions.order_by("start")
    elif order_by == '-start':
        all_auctions = all_auctions.order_by("-start")
    elif order_by == 'end':
        all_auctions = all_auctions.order_by("end")
    elif order_by == '-end':
        all_auctions = all_auctions.order_by("-end")
    elif order_by == 'total':
        all_auctions = all_auctions.order_by("lot_set__count")
    elif order_by == '-total':
        all_auctions = all_auctions.order_by("-lot_set__count")
    

    pager = Paginator(all_auctions, PAGE_ITEMS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        auctions = pager.page(page)
    except (EmptyPage, InvalidPage):
        auctions = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
         
    return render_to_response('auctions/auctions_list.html', 
                              {'auctions': auctions,
                               'total': total,
                               'pages': pager.page_range,
                               'paged': paged,
                               'filter_params': filter_params,
                               'q_title': q_title,
                              }, 
                              RequestContext(request))

    
@shop_admin_required
def inventory_categorize(request):
    return render_to_response('store_admin/inventory/overview.html', {}, 
                              RequestContext(request))


@shop_admin_required
def inventory_item_detail(request):
    return render_to_response('store_admin/inventory/item_detail.html', {},
                              RequestContext(request))

@shop_admin_required
def preferences_overview(request):
    from payments.models import PayPalShopSettings, GoogleCheckoutShopSettings, ManualPaymentShopSettings, BraintreeShopSettings
    shop = request.shop
    
    google = GoogleCheckoutShopSettings.objects.filter(shop=shop).count() > 0
    paypal = PayPalShopSettings.objects.filter(shop=shop).count() > 0
    braintree = BraintreeShopSettings.objects.filter(shop=shop).count() > 0
    manual = ManualPaymentShopSettings.objects.filter(shop=shop).count() > 0
    return render_to_response('store_admin/preferences/overview.html',
                              {'shop' : shop,
                               'google' : google,
                               'paypal' : paypal,
                               'braintree' : braintree,
                               'manual' : manual,                               
                               },
                              RequestContext(request))

@shop_admin_required
def add_profile_photo(request):
    try:
        photo = request.FILES['photo']
        ext = (photo.name.split('.')[1]).lower()
        if ext in ['jpg', 'bmp', 'jpeg', 'gif']:
            shop = request.shop
            profile = shop.owner().get_profile()
            profile.photo = photo
            profile.save()
            request.flash['message'] = "Photo successfully added."
            request.flash['severity'] = "success"
        else:
            request.flash['message'] = "Invalid format!"
            request.flash['severity'] = "error"
    except Exception, e:
        logging.critical("Photo can't be loaded")
        request.flash['message'] = "Photo could not be loaded!"
        request.flash['severity'] = "error"
    return HttpResponseRedirect(reverse("account"))
    
#    
#@shop_admin_required
#def account_username_password(request):
#    return render_to_response('store_admin/account/username_password.html', {},
#                              RequestContext(request))

def ajax_change_qty(request):
    try:
        item_id = request.POST['item_id'].split("_")[1]
        new_qty = int(request.POST['new_qty'])
        
        item = get_object_or_404(Item, pk=item_id)
        item.qty = new_qty
        item.save()
        
    except Exception, e:
        logging.critical(e)
        return HttpResponse("Fallo", status=500)
    
    return HttpResponse()

def ajax_change_price(request):
    import decimal
    try:
        item_id = request.POST['item_id'].split("_")[1]
        new_price = decimal.Decimal(request.POST['new_price'])
        
        item = get_object_or_404(Item, pk=item_id)
        item.price = new_price
        item.save()
        
    except Exception, e:
        logging.critical(e)
        return HttpResponse("Fallo", status=500)
    
    return HttpResponse()