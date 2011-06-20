import logging
import random

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from haystack.query import SearchQuerySet
from market.models import MarketSubCategory, MarketCategory

from auth.decorators import login_required

PRODUCTS_PER_PAGE = 16
ITEMS_PER_PAGE = 20
LOTS_PER_PAGE = 20

def home(request):
    from shops.models import Shop
    from inventory.models import Product
    from market_buy.models import MarketPlacePick, DealerPick

    marketplace = request.marketplace
    market_place_picks = MarketPlacePick.objects.filter(marketplace=marketplace).order_by("order")
    featured_dealers = DealerPick.objects.filter(marketplace=marketplace).order_by("order")[:2]
    recently_products = Product.objects.filter(shop__marketplace=marketplace, has_image=True).order_by("-date_time")[:20]
    
    return render_to_response("%s/home.html" % request.marketplace.template_prefix, 
                              {
                               'market_place_picks' : market_place_picks,
                               'featured_dealers' : featured_dealers,
                               'recently_products' : recently_products,
                               }, 
                              RequestContext(request))

def search(request, category_slug=None, subcategory_slug=None):
    from inventory.models import Product
    
    marketplace = request.marketplace
    
    sqs = SearchQuerySet().models(Product).load_all()
    sqs = sqs.filter(marketplace_id=marketplace.id)

    current_category = None
    current_subcategory = None

    if category_slug:
        current_category = get_object_or_404(
            MarketCategory, slug=category_slug, marketplace=marketplace)
        # narrow search by category_name
        sqs = sqs.filter(category_id=current_category.id)

        if subcategory_slug:
            current_subcategory = get_object_or_404(
                MarketSubCategory, slug=subcategory_slug, 
                parent__id=current_category.id, marketplace=marketplace)
            # narrow search results by subcategory
            sqs = sqs.filter(subcategory_id=current_subcategory.id)

    else:
        category_name = request.GET.get("category", None)
        
        if category_name and category_name != "All Categories":
            sqs = sqs.filter(category__name=category_name)
            # only search for a category when there's a valid category name       
            current_category = get_object_or_404(
                MarketCategory, name=category_name, marketplace=marketplace)
            
    
    getvars = encodevars(request)

    search_text = request.GET.get("q", None)
    if search_text and search_text.strip():        
        sqs = sqs.filter(summary=search_text)
        
    sort_mode = request.session.get("sort_mode", "title")
    
    if sort_mode == "recent":
        sqs = sqs.order_by("-added_at")
    if sort_mode == "oldest":
        sqs = sqs.order_by("added_at")
    if sort_mode == "title":
        sqs = sqs.order_by("title")
    if sort_mode == "-title":
        sqs = sqs.order_by("-title")
    if sort_mode == "price":
        sqs = sqs.order_by("price")
    if sort_mode == "-price":
        sqs = sqs.order_by("-price")
    pager = Paginator(sqs, PRODUCTS_PER_PAGE)

    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        paginator = pager.page(page)
    except (EmptyPage, InvalidPage):
        raise Http404

    paged = (pager.num_pages > 1)

    return render_to_response("%s/search.html" % request.marketplace.template_prefix, 
        {'current_category' : current_category, 'current_subcategory': current_subcategory,
        'products' : paginator, 'pager':pager,
        'paged': paged, 'total': pager.count, 'getvars': getvars,
        'sort_mode' : sort_mode,
        'view_mode' : request.session.get("view_mode", "list")},        
        RequestContext(request))
    
def encodevars(request):
    from django.http import QueryDict
    dic = (request.GET).copy()
    if dic.get("page", None):
        dic.pop("page")
    st = dic.urlencode()
    return st
    
def set_listing_mode(request):
    next = request.GET.get('next', '/')
    mode = request.GET.get('mode', 'gallery')
    request.session['view_mode'] = mode
    return HttpResponseRedirect(next)


def set_order_mode(request):
    next = request.GET.get('next', '/')
    order = request.GET.get('sort', 'title')
    request.session['sort_mode'] = order
    return HttpResponseRedirect(next)


def auctions(request):
    from lots.models import Lot
    marketplace = request.marketplace
    lot_list = Lot.objects.filter(shop__marketplace=marketplace)
    
    pager = Paginator(lot_list, LOTS_PER_PAGE)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        products = pager.page(page)
    except (EmptyPage, InvalidPage):
        products = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response("%s/auctions.html" % request.marketplace.template_prefix, 
                              {
                               'lots' : products,
                               'pages': pager.page_range,
                               'paged': paged,
                               'total': pager.count
                              } , 
                              RequestContext(request))
    
def for_sale(request):
    from for_sale.models import Item
    marketplace = request.marketplace
    item_list = Item.objects.filter(shop__marketplace=marketplace)
    
    pager = Paginator(item_list, ITEMS_PER_PAGE)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        products = pager.page(page)
    except (EmptyPage, InvalidPage):
        products = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response("%s/for_sale.html" % request.marketplace.template_prefix, 
                              {
                               'items' : products,
                               'pages': pager.page_range,
                               'paged': paged,
                               'total': pager.count
                              } , 
                              RequestContext(request))


def sell(request):
    return render_to_response("%s/sell.html" % request.marketplace.template_prefix, 
                              {} , RequestContext(request))

def buy(request):
    
    from inventory.models import Product
    
    marketplace = request.marketplace
    recently_products = Product.objects.filter(shop__marketplace=marketplace, has_image=True).order_by("-date_time")[:20]
    
    return render_to_response("%s/buy.html" % request.marketplace.template_prefix, 
                              {'recently_products' : recently_products} , RequestContext(request))

def community(request):
    return render_to_response("%s/community.html" % request.marketplace.template_prefix, 
                              {} , RequestContext(request))

@login_required
def add_post_comment(request):
    from market.models import MarketBlogPost
    from market.forms import MarketPostCommentForm
    
    if request.method == "POST":
        form = MarketPostCommentForm(request.POST)
        post =  MarketBlogPost.objects.filter(id=request.POST.get("post")).get()
        
        if form.is_valid():
            comment = form.save(commit = False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
    return HttpResponseRedirect(reverse("market_blog"))

def view_post(request, post_slug):
    from market.forms import MarketPostCommentForm
    from market.models import MarketBlogPost
    
    form = MarketPostCommentForm()
    try:
        post = MarketBlogPost.objects.filter(slug=post_slug).get()
    except MarketBlogPost.DoesNotExist:
        return HttpResponse("403")
    
    return render_to_response("%s/post.html" % request.marketplace.template_prefix, 
                              {'post' : post, 'form': form}, RequestContext(request))
                          

def blog(request):
    from market.forms import MarketPostCommentForm
    from market.models import MarketBlogPost, MarketPostComment, MarketPostPick
    
    marketplace = request.marketplace
    
    all_posts = MarketBlogPost.objects.filter(marketplace=marketplace).order_by("-posted_on")
    latest_posts = all_posts[:5]
    latest_comments = MarketPostComment.objects.filter(post__marketplace=marketplace).order_by("-commented_on")[:5]
    picks = MarketPostPick.objects.filter(marketplace=marketplace)
    
    archive = []
    for post in all_posts:
        archive.append({'title': post.title, 'slug': post.slug, 'month' : post.posted_on.strftime("%B")})
    
    form = MarketPostCommentForm()
    
    pager = Paginator(all_posts, 2)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        posts = pager.page(page)
    except (EmptyPage, InvalidPage):
        posts = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    return render_to_response("%s/blog.html" % request.marketplace.template_prefix, 
                              {
                               'archive' : archive,
                               'picks' : picks,
                               'posts' : posts,
                               'latest_posts' : latest_posts,
                               'latest_comments' : latest_comments, 
                               'form' : form,
                               'pages': pager.page_range,
                               'paged': paged,
                               'total': pager.count,
                               } , RequestContext(request))


def contact_us(request):
    
    if request.method == "POST":
        name = request.POST.get('name', 'unknown')
        phone = request.POST.get('phone', 'unknown')
        email = request.POST.get('email', 'unknown')
        message = request.POST.get('message', '- no message -')
        
        msg = "Message from %s (email %s, phone %s).\n%s" % (name, email, phone, message)
        send_mail('Contact Form From %s' % request.marketplace, msg, 'admin@greatcoins.com',  [request.marketplace.contact_email], fail_silently=True)
        
        return HttpResponseRedirect(reverse("market_home"))
    
    return render_to_response("%s/contact_us.html" % request.marketplace.template_prefix, 
                              {} , RequestContext(request))