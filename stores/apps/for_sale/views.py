import datetime
import logging

from django.db.models import Sum
from django.core.urlresolvers import reverse
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auctions.forms import AuctionSessionForm
from auctions.models import AuctionSession 
#from auth.models import User
from market.forms import MarketCategoryForm, MarketSubCategoryForm
from core.decorators import shop_admin_required

#from forms import LotForm, ImageLotForm, CategoryForm, SubCategoryForm
#from models import ImageLot, Lot, Category, SubCategory, Payment, Shipping

from datetime import timedelta

from models import Item, ImageItem
from forms import ItemForm, ImageItemForm

PAGE_ITEMS = 15

@shop_admin_required
def items_all(request):
    shop = request.shop
    items_list = Item.objects.all().filter(shop=shop).order_by("-date_time")

    pager = Paginator(items_list, PAGE_ITEMS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        items = pager.page(page)
    except (EmptyPage, InvalidPage):
        items = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response('for_sale/items_all.html', 
                              {'items': items,
                               'pages': pager.page_range,
                               'paged': paged,
                               }, 
                              RequestContext(request)) 

@shop_admin_required
def items_bulk_delete(request):
    
    ids = request.POST
    for (item_id, status) in ids.items():
        if status == "on": 
            item = get_object_or_404(Item, pk=item_id)
            item.delete()
    Item.update_latest_item(request.shop)
    
    request.flash['message'] = unicode(_("Items removed"))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse("inventory_items"))
    
@shop_admin_required
def item_add(request):
    shop = request.shop
    
    items_plan_limit = shop.plan().concurrent_store_items
    if shop.total_items() >= items_plan_limit:
        request.flash['message'] = "You have reached the limit of items that can hold simultaneously."
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('inventory_items'))
        
    if request.method == 'POST':
        form = ItemForm(request, request.POST, request.FILES, prefix="item")
        if form.is_valid():
            item = form.save(commit=False)
            item.shop = request.shop
            item.save()
            Item.update_latest_item(shop)
            for img in request.FILES.getlist('file'):
                image = ImageItem()
                image.item = item
                image.image.save(img.name,img)
            request.flash['message'] = unicode(_("Item successfully added."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('inventory_items'))
    else:
        form = ItemForm(request, prefix="item")
    form_category = MarketCategoryForm(prefix="category")
    form_sub_category = MarketSubCategoryForm(request, prefix="sub_category")
    form_session = AuctionSessionForm(prefix="session")
    sessions = AuctionSession.objects.filter(shop = request.shop)
    return render_to_response('for_sale/item_add.html', 
                              {'form': form,
                               'form_category': form_category,
                               'form_sub_category': form_sub_category,
                               'form_session': form_session,
                               'sessions': sessions,
                               },
                              RequestContext(request))

@shop_admin_required
def import_inventory(request):
    from models import PCGSNumberException
    shop = request.shop
    failures = []
    if request.method == 'POST':
        remove_inventory = bool(request.POST['r'] == "True")
        if remove_inventory:
            items = Item.objects.filter(shop=shop)
            for item in items:
                item.delete()
        
        for file in request.FILES.getlist('file'):
            try:
                from xls_parser import CoinInventoryParser
                parser = CoinInventoryParser()
                (keys, products) = parser.parse_xls(file)
                
                for product in products:
                    if product == []: continue
                    try:
                        Item.create_from_inventory(shop, keys, product)
                    except PCGSNumberException as e:
                        logging.critical("PCGSNumber not exists for product %s" % product)
                        failures.append(u"Product Number: %s, Error: %s<br>" % (product[0], e.parameter))
            except Exception, e:
                logging.error(e)

    if len(failures) > 0:
        request.flash['message'] = u"Fail when trying to load the Inventory. These items could not be loaded:<br>"
        for message in failures:
            request.flash['message'] += message
        request.flash['severity'] = "error"    
    else:
        request.flash['message'] = "Inventory successfully added."
        request.flash['severity'] = "success"    
    
    return HttpResponseRedirect(reverse('inventory_items'))

#@shop_admin_required
#def item_details(request, item_id):
#    logging.critical("llego")
#    try:
#        item = get_object_or_404(Item, pk=item_id)
#        if item.shop != request.shop:
#            raise Http404
#        image_form = ImageItemForm()
#        params = {'item': item, 'image_form': image_form }
#        return render_to_response('for_sale/item_details.html', params, RequestContext(request))
#    except Exception, e:
#        logging.critical(e)


#@shop_admin_required
#def item_details(request, item_id):
#    logging.critical('%s%s%s' %('\n'*3, '*'*120, '\n'*3))
#    try:
#        item = get_object_or_404(Item, pk=item_id)
#        if item.shop != request.shop:
#            raise Http404
#        image_form = ImageItemForm()
#        params = {'item': item, 'image_form': image_form }
#        return render_to_response('for_sale/item_details.html', params, RequestContext(request))
#    except Exception, e:
#        logging.critical(e)

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
def item_details(request, item_id):
    try:
        item = get_object_or_404(Item, pk=item_id)
        if item.shop != request.shop:
            raise Http404
        image_form = ImageItemForm()
        params = {'item': item, 'image_form': image_form }
        return render_to_response('for_sale/item_details.html', params, RequestContext(request))
    except Exception, e:
        logging.critical(e)


@shop_admin_required
def add_img(request, item_id):
    try:
        item = get_object_or_404(Item, pk=item_id, shop=request.shop)
        data = []
        if request.method == 'POST':
            limit = request.shop.get_limit('pictures_per_item')
            total = ImageItem.objects.filter(item=item).count()
            
            f = request.FILES.get('files')
            if f and not (total >= limit):
                image = ImageItem(item=item)
                image.image.save(f.name, f)
                item.save()
                
                data = [{
                        'name': f.name, 
                        'url': image.image.url,
                        'size': image.image.size, 
                        'thumbnail_url': image.image.url_100x100,
                        'delete_url': reverse('del_item_image', args=[image.id]), 
                        'delete_type': "DELETE",
                        'url_set_primary': reverse('set_forsale_primary_picture', args=[item_id, image.id])
                }]
            else:
                data = [{'error': 'You have reach the limit of pictures per item allowed by your plan!'}]
        else:
            for image in item.imageitem_set.all():
                data.append({
                             'name': image.image.name,
                             'url': image.image.url,
                             'size': image.image.size,
                             'thumbnail_url': image.image.url_100x100,
                             'delete_url': reverse('del_item_image', args=[image.id]), 
                             'delete_type': "DELETE",
                             'is_primary': image.primary_picture,
                             'url_set_primary': reverse('set_forsale_primary_picture', args=[item_id, image.id]) 
                })

        response = JSONResponse(data, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    except Exception, ex:
        logging.exception(str(ex))
#        return HttpResponseRedirect(reverse('item_details', args=[item_id]))


@shop_admin_required
def remove_img(request, id):
    image = get_object_or_404(ImageItem, pk=int(id))
    image.delete()
    
    response = JSONResponse(True, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


#@shop_admin_required
def item_delete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if item.shop != request.shop:
        raise Http404
    item.delete()
    Item.update_latest_item(request.shop)
    
    request.flash['message'] = unicode(_("Item successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse("inventory_items"))

@shop_admin_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if item.shop != request.shop:
        raise Http404

    if request.method == 'POST':
        form = ItemForm(request, request.POST, request.FILES, prefix="item", instance=item)
        if form.is_valid():
            item = form.save()
#            for img in request.FILES.getlist('file'):
#                image = ImageItem()
#                image.item = item
#                image.image.save(img.name,img)
            request.flash['message'] = unicode(_("Item successfully edited. It might take a half hour to reflect the proper search results."))
            request.flash['severity'] = "success"
        else:
            request.flash['message'] = unicode(_("Item couldn't be edited."))
            request.flash['severity'] = "error"
        
        return HttpResponseRedirect(reverse('inventory_items'))
    else:
        form = ItemForm(request, prefix="item", instance=item)
    
    form_category = MarketCategoryForm(prefix="category")
    form_sub_category = MarketSubCategoryForm(request, prefix="sub_category")
    
    return render_to_response('for_sale/item_edit.html', 
                              {'form': form,
                               'item': item,
                               'form_category': form_category,
                               'form_sub_category': form_sub_category,
                               },
                              RequestContext(request))

#@shop_admin_required
#def add_item_image(request, item_id):
#        
#    if request.method == 'POST':
#        
#        shop = request.shop
#        item = get_object_or_404(Item, pk=item_id)
#        
#        limit = shop.get_limit('pictures_per_item')
#        total = ImageItem.objects.filter(item=item).count()
#        
#        if total >= limit:
#            logging.info("User reach the pictures per item plan limit")
#            request.flash['message'] = "You have reach the limit of pictures per item allowed by your plan!"
#            request.flash['severity'] = "error"
#        else:
#            form = ImageItemForm(request.POST, request.FILES)
#            if form.is_valid():
#                img = form.save(commit=False)
#                img.item = item
#                img.save()
#                request.flash['message'] = "Image successfully saved!"
#                request.flash['severity'] = "success"
#            
#            else:
#                logging.error(form.errors)
#                request.flash['message'] = form.errors
#                request.flash['severity'] = "error"
#        
#        return HttpResponseRedirect(reverse('item_details', args=[item_id]))
#    
#    else:
#        raise Http404

# orig:
@shop_admin_required
def add_item_image(request, item_id):
        
    if request.method == 'POST':
        shop = request.shop
        item = get_object_or_404(Item, pk=item_id)
        
        limit = shop.get_limit('pictures_per_item')
        total = ImageItem.objects.filter(item=item).count()
        
        if total >= limit:
            logging.info("User reach the pictures per item plan limit")
            request.flash['message'] = "You have reach the limit of pictures per item allowed by your plan!"
            request.flash['severity'] = "error"
        else:
            form = ImageItemForm(request.POST, request.FILES)
            if form.is_valid():
                img = form.save(commit=False)
                img.item = item
                img.save()
                request.flash['message'] = "Image successfully saved!"
                request.flash['severity'] = "success"
            
            else:
                logging.error(form.errors)
                request.flash['message'] = form.errors
                request.flash['severity'] = "error"
        
        return HttpResponseRedirect(reverse('item_details', args=[item_id]))
    
    else:
        raise Http404

#@shop_admin_required
#def add_item_image(request, item_id):
## wip jquery upload
#    if request.method == 'POST':
#        shop = request.shop
#        item = get_object_or_404(Item, pk=item_id)
#        
#        limit = shop.get_limit('pictures_per_item')
#        total = ImageItem.objects.filter(item=item).count()
#        
#        if total >= limit:
#            logging.info("User reach the pictures per item plan limit")
#            request.flash['message'] = "You have reach the limit of pictures per item allowed by your plan!"
#            request.flash['severity'] = "error"
#        else:
#            f = request.FILES.get('files')
#
#        return HttpResponseRedirect(reverse('item_details', args=[item_id]))
#    
#    else:
#        raise Http404


@shop_admin_required
def del_item_image(request, item_id, image_id):
    image = get_object_or_404(ImageItem, pk=image_id)
    image.delete()
    
    item = image.item
    if ImageItem.objects.filter(item=item).count() == 0:
        item.has_image = False
        item.save()
        
    return HttpResponseRedirect(reverse('item_details', args=[item_id]))

#@shop_admin_required
#def product_remove_image(request, id):
#    imagen_product = get_object_or_404(ImageProduct, pk=int(id), shop=request.shop)
#    imagen_product.delete()
#    
#    response = JSONResponse(True, {}, response_mimetype(request))
#    response['Content-Disposition'] = 'inline; filename=files.json'
#    return response

@shop_admin_required
def set_primary_picture(request, item_id, image_id):
    item = get_object_or_404(Item, pk=item_id)
    images = ImageItem.objects.filter(item=item)
    for image in images:
        image.primary_picture= False
        image.save()
        
    image = get_object_or_404(ImageItem, pk=image_id)
    image.primary_picture = True
    image.save()
    
    return HttpResponseRedirect(reverse('item_details', args=[item_id]))

