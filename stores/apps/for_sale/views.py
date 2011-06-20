import datetime
import logging

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
    request.flash['message'] = unicode(_("Items removed"))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse("inventory_items"))
    
@shop_admin_required
def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request, request.POST, request.FILES, prefix="item")
        if form.is_valid():
            item = form.save(commit=False)
            item.shop = request.shop
            item.save()
            item.update_latest_item()
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
    return render_to_response('store_admin/inventory/item_add.html', 
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
                    except PCGSNumberException:
                        logging.critical("PCGSNumber not exists for product %s" % product)
                        failures.append(product[0])
                    
            except Exception, e:
                logging.error(e)
    
    if len(failures) > 0:
        request.flash['message'] = "Fail when trying to load the Inventory. These items could not be loaded : %s" % failures
        request.flash['severity'] = "error"    
    else:
        request.flash['message'] = "Inventory successfully added."
        request.flash['severity'] = "success"    
    
    return HttpResponseRedirect(reverse('inventory_items'))

@shop_admin_required
def item_details(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if item.shop != request.shop:
        raise Http404
    image_form = ImageItemForm()
    return render_to_response('store_admin/inventory/item_details.html', 
                              {'item': item,
                               'image_form': image_form,
                               },
                              RequestContext(request))
    
@shop_admin_required
def item_delete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if item.shop != request.shop:
        raise Http404
    item.delete()
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
            request.flash['message'] = unicode(_("Item successfully edited."))
            request.flash['severity'] = "success"
        else:
            request.flash['message'] = unicode(_("Item couldn't be edited."))
            request.flash['severity'] = "error"
        
        return HttpResponseRedirect(reverse('inventory_items'))
    else:
        form = ItemForm(request, prefix="item", instance=item)
    
    form_category = MarketCategoryForm(prefix="category")
    form_sub_category = MarketSubCategoryForm(request, prefix="sub_category")
    
    return render_to_response('store_admin/inventory/item_edit.html', 
                              {'form': form,
                               'item': item,
                               'form_category': form_category,
                               'form_sub_category': form_sub_category,
                               },
                              RequestContext(request))

@shop_admin_required
def add_item_image(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ImageItemForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.item = item
            img.save()
        else:
            logging.error(form.errors)
            request.flash['message'] = form.errors
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('item_details', args=[item_id]))
    
    return HttpResponseRedirect(reverse('item_details', args=[item_id]))


@shop_admin_required
def del_item_image(request, item_id, image_id):
    image = get_object_or_404(ImageItem, pk=image_id)
    image.delete()
    
    item = image.item
    if ImageItem.objects.filter(item=item).count() == 0:
        item.has_image = False
        item.save()
        
    return HttpResponseRedirect(reverse('item_details', args=[item_id]))

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

