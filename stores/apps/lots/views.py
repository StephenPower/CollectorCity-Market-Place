import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auctions.forms import AuctionSessionForm
from auctions.models import AuctionSession 
from core.decorators import shop_admin_required

from lots.forms import LotForm, ImageLotForm 
from market.forms import MarketCategoryForm, MarketSubCategoryForm
from models import ImageLot, Lot

PAGE_LOTS = 10
   

@shop_admin_required
def lots_all(request):
    shop = request.shop
    lot_list = Lot.objects.all().filter(shop=shop).order_by("-date_time")

    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response('lots/lots_all.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request))    


@shop_admin_required
def lots_active(request):
    shop = request.shop
    lot_list = Lot.objects.all().filter(shop=shop, state='A').order_by("-date_time")

    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)

    return render_to_response('lots/lots_active.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request))    

@shop_admin_required
def lots_sold(request):
    shop = request.shop
    lot_list = Lot.objects.all().filter(shop=shop, state='S').order_by("-date_time")
    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)

    return render_to_response('lots/lots_sold.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request))    


@shop_admin_required
def lots_didnt_sell(request):
    shop = request.shop
    lot_list = Lot.objects.all().filter(shop=shop, state='N').order_by("-date_time")
    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    return render_to_response('lots/lots_didnt_sell.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request))    


@shop_admin_required
def lots_payment_all(request):
    shop = request.shop
    lot_list = Lot.objects.filter(shop=shop, state='S').order_by("-id")
    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    return render_to_response('lots/lots_payment_all.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request)) 

@shop_admin_required
def lots_shipping_all(request):
    shop = request.shop
    lot_list = Lot.objects.filter(shop=shop, state='S').order_by("-id")
    pager = Paginator(lot_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    return render_to_response('lots/lots_shipping_all.html', 
                              {'lots': lots,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request)) 


@shop_admin_required
def lots_dispatched(request, id):
    lot = get_object_or_404(Lot, pk=id)
    shop = request.shop
    if lot.shop != shop:
        raise Http404
    lot.shipping().dispatched()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('lots_shipping_all'))


@shop_admin_required
def lots_fulfilled(request, id):
    lot = get_object_or_404(Lot, pk=id)
    shop = request.shop
    if lot.shop != shop:
        raise Http404
    lot.shipping().fulfilled()
    request.flash['message'] = unicode(_("Operation successfully saved."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('lots_shipping_all'))    
    
    
@shop_admin_required
def lots_open(request):
    return render_to_response('lots/lots_open.html', {}, 
                              RequestContext(request))    


@shop_admin_required
def lots_closed(request):
    return render_to_response('lots/lots_closed.html', {}, 
                              RequestContext(request))    


@shop_admin_required
def lot_details(request, lot_id):
    lot = get_object_or_404(Lot, pk=lot_id)
    shop = request.shop
    if lot.shop != shop:
        raise Http404
    image_form = ImageLotForm()
    return render_to_response('lots/lot_details.html', 
                              {'lot': lot,
                               'image_form': image_form,
                               },
                              RequestContext(request))
    

@shop_admin_required
def lot_edit(request, lot_id):
    lot = get_object_or_404(Lot, pk=lot_id)
    shop = request.shop
    if lot.shop != shop:
        raise Http404
    
    if request.method == 'POST':
        form = LotForm(request, request.POST, prefix="lot", instance=lot)
        if form.is_valid():
            lot = form.save()
#            for img in request.FILES.getlist('file'):
#                image = ImageLot(image = img, lot=lot)
#                image.save()
#                image.lot = lot
#                image.image.save(img.name,img)
            request.flash['message'] = unicode(_("Lot successfully updated. It might take a half hour to reflect the proper search results."))
            request.flash['severity'] = "success"
        else:
            request.flash['message'] = unicode(_("Lot couldn't be updated."))
            request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('inventory_lots'))
    else:
        form = LotForm(request, prefix="lot", instance=lot)
    
    form_category = MarketCategoryForm(prefix="category")
    form_sub_category = MarketSubCategoryForm(request, prefix="sub_category")
    form_session = AuctionSessionForm(prefix="session")
    sessions = AuctionSession.objects.filter(shop = request.shop)
    return render_to_response('lots/lot_edit.html', 
                              {'form': form,
                               'form_category': form_category,
                               'form_sub_category': form_sub_category,
                               'form_session': form_session,
                               'lot': lot,
                               'sessions': sessions,
                               },
                              RequestContext(request))

    
@shop_admin_required
def lot_add(request):
    
    if request.method == 'POST':
        form = LotForm(request, request.POST, prefix="lot")
        if form.is_valid():
            lot = form.save(commit=False)
            lot.shop = request.shop
            lot.state = 'A'
            lot.save()
            for img in request.FILES.getlist('file'):
                image = ImageLot(image = img, lot=lot)
                image.save()
#                image.lot = lot
#                image.image.save(img.name,img)
            request.flash['message'] = unicode(_("Lot successfully added."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('inventory_lots'))
    else:
        form = LotForm(request, prefix="lot")
    form_category = MarketCategoryForm(prefix="category")
    form_sub_category = MarketSubCategoryForm(request, prefix="sub_category")
    form_session = AuctionSessionForm(prefix="session")
    
    return render_to_response('lots/lot_add.html', 
                              {'form': form,
                               'form_category': form_category,
                               'form_sub_category': form_sub_category,
                               'form_session': form_session,
                               },
                              RequestContext(request))


@shop_admin_required
def set_primary_picture(request, lot_id, image_id):
    lot = get_object_or_404(Lot, pk=lot_id)
    images = ImageLot.objects.filter(lot=lot)
    for image in images:
        image.primary_picture= False
        image.save()
        
    image = get_object_or_404(ImageLot, pk=image_id)
    image.primary_picture = True
    image.save()
    
    return HttpResponseRedirect(reverse('lot_details', args=[lot_id]))


#@shop_admin_required
#def add_image(request, lot_id):
#    
#    if request.method == 'POST':
#        shop = request.shop
#        lot = get_object_or_404(Lot, pk=lot_id)
#    
#        limit = shop.get_limit('pictures_per_lot')
#        total = ImageLot.objects.filter(lot=lot).count()
#            
#        if total >= limit:
#            request.flash['message'] = "You have reach the limit of pictures per lot allowed by your plan!"
#            request.flash['severity'] = "error"
#        
#        else:
#            form = ImageLotForm(request.POST, request.FILES)
#            if form.is_valid():
#                img = form.save(commit=False)
#                img.lot = lot
#                img.save()
#                request.flash['message'] = "Image successfully saved!"
#                request.flash['severity'] = "success"
#            else:
#                request.flash['message'] = "You have reach the limit of pictures per lot allowed by your plan!"
#                request.flash['severity'] = "error"
#        
#        return HttpResponseRedirect(reverse('lot_details', args=[lot_id]))
#    else:
#        raise Http404

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
        
@shop_admin_required
def add_img(request, lot_id):
    try:
        lot = get_object_or_404(Lot, pk=lot_id, shop=request.shop)
        data = []
        if request.method == 'POST':
            limit = request.shop.get_limit('pictures_per_lot')
            total = ImageLot.objects.filter(lot=lot).count()

            f = request.FILES.get('files')
            if f and not (total >= limit):
                image = ImageLot(lot=lot)
                image.image.save(f.name, f)
                lot.save()

                data = [{
                        'name': f.name, 
                        'url': image.image.url,
                        'size': image.image.size, 
                        'thumbnail_url': image.image.url_100x100,
                        'delete_url': reverse('del_image', args=[lot_id, image.id]), 
                        'delete_type': "DELETE",
                        'url_set_primary': reverse('set_lot_primary_picture', args=[lot_id, image.id])
                }]
            else:
                data = [{'error': 'You have reach the limit of pictures per lot allowed by your plan!' }]
        else:
            for image in lot.imagelot_set.all():
                data.append({
                             'name': image.image.name,
                             'url': image.image.url,
                             'size': image.image.size,
                             'thumbnail_url': image.image.url_100x100,
                             'delete_url': reverse('del_image', args=[lot_id, image.id]), 
                             'delete_type': "DELETE",
                             'is_primary': image.primary_picture,
                             'url_set_primary': reverse('set_lot_primary_picture', args=[lot_id, image.id]) 
                })

        response = JSONResponse(data, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        
        return response
    except Exception, ex:
        logging.exception(str(ex))


@shop_admin_required
def del_image(request, lot_id, image_id):
    image = get_object_or_404(ImageLot, pk=image_id)
    image.delete()
    lot = image.lot
    if ImageLot.objects.filter(lot=lot).count() == 0:
        lot.has_image = False
        lot.save()
    
    return HttpResponseRedirect(reverse('lot_details', args=[lot_id]))
