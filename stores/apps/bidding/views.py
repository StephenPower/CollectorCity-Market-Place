# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.template.defaultfilters import striptags, date
from django.utils.translation import ugettext as _

from auctions.models import AuctionSession
from bidding.forms import BiddingSearchForm, BidForm
from blog_pages.models import Post, About, Home, Page, DynamicPageContent
from core.decorators import shop_required, auctions_feature_required
from for_sale.models import Item
from lots.models import Lot
from shops.models import MailingListMember
from sell.templatetags.sell_tags import money_format
from sell.models import Cart
from themes.models import Asset

from jinja2 import Environment
from jinja2.loaders import BaseLoader


PAGE_SEARCH = 10
PAGE_BLOG = 3
PAGE_LOTS = 6


class ThemeLoader(BaseLoader):

    def __init__(self, shop, is_secure=False):
        self.shop = shop
        self.is_secure = is_secure 

    def get_source(self, environment, template):
        source = self.shop.theme.get_template(template)
        path = "%s/%s" % (self.shop.name, template)
        return source, path, lambda: False
    
    def asset_url(self, name_file):
        try:
            asset = Asset.objects.filter(theme__shop=self.shop, name=name_file)[0]
            if asset.is_editable():
                if self.is_secure:
                    return settings.SECURE_ASSET_URL + asset.assetrenderingsecure.file.name
                else:
                    return asset.assetrendering.file.url
            else:
                if self.is_secure:
                    return settings.SECURE_ASSET_URL + asset.file.name
                else:
                    return asset.file.url
        except:
            logging.error("Asset(%s) object not found" % name_file)
            return ''


@shop_required
def my_render(request, param, name_page=None):
    """ news_items """
    items = Item.objects.filter(shop=request.shop).order_by('-id')[:10] 
    new_items = []
    for i in items:
        image = i.image()
        plain_item = {
            'title': i.title,
            'description': i.description,
            'price': money_format(i.price, request.shop), 
            'url': reverse('bidding_view_item', args=[i.id]),
            'image': {'original': image.image.url if image else "",
                      'small': image.image.url_100x100 if image else "",
                      'medium': image.image.url_400x400 if image else "",
                      } 
        }
        new_items.append(plain_item)

    """ Sessions """
    sessions = AuctionSession.objects.filter(shop=request.shop, end__gte=datetime.now())        
    sessions_list = []
    sessions_list.append({'title': 'Highlights', 'url': reverse('bidding_auctions')})
    for session in sessions:
        sessions_list.append({
                             'title': session.title,
                             'url': reverse('bidding_auctions_id', args=[session.id]),
                             })
   
    """ Menu """
    t = loader.get_template('bidding/blocks/menu_menu.html')
    c = RequestContext(request, {'shop':request.shop})
    menu = (t.render(c))

    """ Header """
    t = loader.get_template('bidding/blocks/header.html')
    c = RequestContext(request, {'shop':request.shop})
    header = (t.render(c))

    """ Footer """
    t = loader.get_template('bidding/blocks/footer.html')
    c = RequestContext(request, {'shop':request.shop})
    footer = (t.render(c))
    
    about = request.shop.about.body
    links = []
    
    menus = request.shop.menu_set.all()
    if menus.count() > 0:
        for link in menus[0].links():
            if link.to == "/auctions/" and not request.shop.auctions_feature_enabled():
                continue
            links.append({
                  'to': link.to,
                  'name': link.name,
            })
        
    """ Flash """
    t = loader.get_template('bidding/blocks/flash.html')
    c = RequestContext(request, {})
    flash = (t.render(c))

    """ Posts """
    last = request.shop.last_post()
    if last:
        last_post = {'url': reverse('bidding_view_post', args=[last.id]),
                     'title': last.title,
                     'body': last.body,
                     'date_time': date(last.date_time,'F j, Y'),
                    }
    else:
        last_post = {}

    env = Environment(loader=ThemeLoader(request.shop, request.is_secure()))
    env.filters['asset_url'] = env.loader.asset_url
    

    if name_page:
        try:
            template = env.get_template(name_page)
            content = template.render(param)
        except Exception, e:
            return HttpResponse("Error in template %s. %s" % (name_page, e))
    else:
        content = param.get('block')
    
    if request.user.is_authenticated():
        try:
            cart = Cart.objects.filter(shop=request.shop, bidder=request.user).get()
            total_cart_items = cart.total_items()
        except Cart.DoesNotExist:
            total_cart_items = 0
    else:
        total_cart_items = 0
    
    param_default = {
                     'about': about,
                     'content': content,
                     'flash': flash,
                     'footer': footer,  
                     'header': header,
                     'last_post': last_post,
                     'links': links,
                     'new_items': new_items,
                     'menu': menu,
                     'page_title': param.get('page_title', ''),
                     'page_description': param.get('page_description', ''),
                     'total_cart_items': total_cart_items,
                     'url_my_shopping': reverse('my_shopping'),
                     'url_my_orders': reverse('my_orders'),
                     'url_search': reverse('bidding_search'),
                     'user_is_logged': request.user.is_authenticated() and not request.shop.is_admin(request.user),
                     'shop_name': request.shop.name_shop(),
                     'sessions': sessions_list,
                     }

    try:
        template = env.get_template('layout')
        html = template.render(param_default)
    except Exception, e:
        return HttpResponse("Error in template layout. %s" %  e)
    
    return html


@shop_required
def bidding_home(request):
    from shops.forms import MailingListMemberForm
    
    logging.critical(request.GET.get("u", None))
    shop = request.shop
    if request.method == "POST":
        
        form = MailingListMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.shop = shop
            member.save()
            request.flash['message'] = unicode(_("Email successfully registered."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse("home"))
    else:
        form = MailingListMemberForm()

    t = loader.get_template('bidding/blocks/mailing_list_form.html')
    c = RequestContext(request, {'form' : form})
    block_mailing_list = (t.render(c))
    
    home = Home.objects.filter(shop=request.shop).get()
    
    #TODO: replace collections
    """ news_items """
    items = Item.objects.filter(shop=request.shop).order_by('-id')[:10] 
    new_items = []
    for i in items:
        image = i.image()
        new_items.append({
            'title': i.title,
            'description': i.description,
            'price': money_format(i.price, request.shop), 
            'url': reverse('bidding_view_item', args=[i.id]),
            'image': {'original': image.image.url if image else "",
                      'small': image.image.url_100x100 if image else "",
                      'medium': image.image.url_400x400 if image else "",
                      } 
            })

    last = request.shop.last_post()
    if last:
        last_post = {'url': reverse('bidding_view_post', args=[last.id]),
                     'title': last.title,
                     'body': last.body,
                     'date_time': date(last.date_time,'F j, Y'),
                    }
    else:
        last_post = {}        
        
    """ Sessions """
    sessions = AuctionSession.objects.filter(shop=request.shop, end__gte=datetime.now())        
    new_sessions = []
    new_sessions.append({'title': 'Highligths', 'url': reverse('bidding_auctions')})
    for session in sessions:
        new_sessions.append({
                             'title': session.title,
                             'url': reverse('bidding_auctions_id', args=[session.id]),
                             })        

    about = request.shop.about.body

    param = {
             'about': about,
             'home': 
                {
                 'title': home.title, 
                 'body': home.body, 
                 'image': home.image
                 },
             'last_post': last_post,
             'mailing_list': block_mailing_list,
             'new_items': new_items,
             'page_title': 'Home',
             'page_description': striptags(home.meta_content),
             'sessions': new_sessions,
            }
        
    return HttpResponse(my_render(request, param, 'home'))
    
    
    
@shop_required
def bidding_for_sale(request):
    items_list = Item.objects.filter(shop=request.shop, qty__gt=0)
        
    pager = Paginator(items_list, PAGE_LOTS)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1        
    try:
        items = pager.page(page)
    except (EmptyPage, InvalidPage):
        items = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    items_list = []
    for item in items.object_list:
        image = item.image()
        items_list.append({'url': reverse('bidding_view_item', args=[item.id]),
                          'title': item.title,
                          'price': money_format(item.price, request.shop),
                          'image': {'original': image.image.url if image else None,
                                    'small': image.image.url_100x100 if image else None,
                                    'medium': image.image.url_400x400 if image else None,
                                    } 
                          })

    t = loader.get_template('paginator.html')
    c = RequestContext(request, {'objects': items,
                                 'pages': pager.page_range,
                                 'paged': paged,})
    paginator = (t.render(c))
    
    try:
        page = DynamicPageContent.objects.filter(shop=request.shop, page="for_sale").get()
        description = striptags(page.meta_content)
    except DynamicPageContent.DoesNotExist:
        description = "No meta description found"
    
    param = {
             'items': items_list, 
             'paginator': paginator,
             'page_title': 'For Sale',
             'page_description': description,
             } 
    return HttpResponse(my_render(request, param, 'for_sale'))
    
    

@shop_required
@auctions_feature_required
def bidding_auctions(request, session_id=None):
    
    if session_id:
        session = get_object_or_404(AuctionSession, pk=session_id)
        lots = Lot.objects.filter(shop=request.shop, session=session, state='A')
        session_title = session.title
    else:
        session_title = 'Highlights'
        lots = Lot.objects.filter(shop=request.shop, state='A')
        
    pager = Paginator(lots, PAGE_LOTS)  
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1        
    try:
        lots = pager.page(page)
    except (EmptyPage, InvalidPage):
        lots = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)

    lots_list = []
    for lot in lots.object_list:
        image = lot.image()
        lots_list.append({'url': reverse('bidding_view_lot', args=[lot.id]),
                          'title': lot.title,
                          'price': money_format(lot.price(), request.shop),
                          'image': {'original': image.image.url if image else None,
                                    'small': image.image.url_100x100 if image else None,
                                    'medium': image.image.url_400x400 if image else None,
                                   } 
                         })

    sessions = AuctionSession.objects.filter(shop=request.shop, end__gte=datetime.now())
    t = loader.get_template('bidding/blocks/sessions.html')
    c = RequestContext(request, {'sessions': sessions})
    block_sessions = (t.render(c))

    t = loader.get_template('paginator.html')
    c = RequestContext(request, {'objects': lots,
                                 'pages': pager.page_range,
                                 'paged': paged,})
    paginator = (t.render(c))
    
    try:
        page = DynamicPageContent.objects.filter(shop=request.shop, page="auctions").get()
        description = striptags(page.meta_content)
    except DynamicPageContent.DoesNotExist:
        description = "No meta description found"
        
    param = {
             'lots': lots_list,
             'sessions': block_sessions,
             'session_title': session_title,    
             'paginator': paginator,
             'page_title': 'Auctions',
             'page_description': description,
             } 

    return HttpResponse(my_render(request, param, 'auctions'))
    


@shop_required
def bidding_blog(request):
    list_posts = Post.objects.filter(shop=request.shop).filter(draft=False).order_by("-date_time") 
    last_posts = list_posts[:5]

    pager = Paginator(list_posts, PAGE_BLOG)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1        
    try:
        posts = pager.page(page)
    except (EmptyPage, InvalidPage):
        posts = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    last_post_list = []
    for p in last_posts:
        last_post_list.append({'title': p.title,
                               'url': reverse('bidding_view_post', args=[p.id]),
                               'date_time': date(p.date_time, 'F j, Y'),
                               'body': p.body,
                               })  

    posts_list = []
    for p in posts.object_list:
        posts_list.append({'title': p.title,
                          'url': reverse('bidding_view_post', args=[p.id]),
                          'date_time': date(p.date_time, 'F j, Y'),
                          'body': p.body, 
                         })

    t = loader.get_template('paginator.html')
    c = RequestContext(request, {'objects': posts,
                                 'pages': pager.page_range,
                                 'paged': paged,})
    paginator = (t.render(c))
    
    try:
        page = DynamicPageContent.objects.filter(shop=request.shop, page="blog").get()
        description = striptags(page.meta_content)
    except DynamicPageContent.DoesNotExist:
        description = "No meta description found"
        
    param = {
             'posts': posts_list, 
             'last_posts': last_post_list, 
             'paginator': paginator,
             'page_title': 'Blog',
             'page_description': description
             }
    
    return HttpResponse(my_render(request, param, 'blog'))

    
    
@shop_required
def bidding_about_us(request):
    about = About.objects.filter(shop=request.shop).get()
    
    t = loader.get_template('bidding/blocks/map.html')
    c = RequestContext(request, {'about': about})
    block_map = (t.render(c))
    
    param = {
             'about': 
                {'title': about.title, 'body': about.body, 'location': request.shop.location},
             'map': block_map,
             'page_title': 'About Us',
             'page_description': '%s' % striptags(about.meta_content) 
            }
    
    return HttpResponse(my_render(request, param, 'about_us'))



@shop_required
def bidding_view_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.visited()
    
    if post.meta_content: description = striptags(post.meta_content)
    else: description = post.title
        
    param = {
             'post': 
                {'title': post.title, 'body': post.body, 'date_time': post.date_time},
             'url': reverse('bidding_blog'),
             'page_title': post.title,
             'page_description': '%s' % description
            }

    return HttpResponse(my_render(request, param, 'view_post'))
    

@shop_required
def bidding_view_lot(request, id):
    #TODO: filter by state lot
    #TODO: add csrf_token to form
    lot = get_object_or_404(Lot, pk=id)
    
    request.shop.add_view()

    form = BidForm(lot, request.GET or None)
    if form.is_valid():
        
        if (not request.user.is_authenticated()) or request.user.is_staff or request.user.is_superuser:
            return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())
        if not (lot.is_active() and lot.shop == request.shop):
            raise Http404
        
        
        lot.bid(request.user, form.cleaned_data['amount'], request.META['REMOTE_ADDR'])
        
        request.flash['message'] = unicode(_("Bid successfully registered."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('bidding_view_lot', args=[id]))
            
    t = loader.get_template('bidding/blocks/view_lot_form.html')
    c = RequestContext(request, {'form': form, 'lot': lot})
    block_view_lot_form = (t.render(c))

    images = []
    for img in lot.imagelot_set.all():
        images.append({
                       'original': img.image.url if img else None,
                       'small': img.image.url_100x100 if img else None,
                       'medium': img.image.url_400x400 if img else None,
                      })
    
    param = {
             'lot': 
                {'title': lot.title,
                 'category': lot.category.name,
                 'subcategory': lot.subcategory.name if lot.subcategory else "",
                 'time_left': lot.time_left(), 
                 'session_end': lot.session.end, 
                 'description': lot.description, 
                 },
              'user_is_logged': request.user.is_authenticated() and not request.shop.is_admin(request.user),
              'form': block_view_lot_form, 
              'images': images,
              'page_title': lot.title,
              'page_description': '%s, %s' % (lot.title, striptags(lot.description))
            }
    
    return HttpResponse(my_render(request, param, 'view_lot'))
    
    
@shop_required
def bidding_view_history_lot(request, id):
    #TODO: filter by state lot
    #TODO: add csrf_token to form    
    lot = get_object_or_404(Lot, pk=id)
    form = BidForm(lot, request.GET or None)
    if form.is_valid():
        if (not request.user.is_authenticated()) or request.user.is_staff or request.user.is_superuser:
            return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())
        if not (lot.is_active() and lot.shop == request.shop):
            raise Http404
        
        lot.bid(request.user, form.cleaned_data['amount'], request.META['REMOTE_ADDR'])

        request.flash['message'] = unicode(_("Bid successfully registered."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('bidding_view_history_lot', args=[id]))

    history = []
    for bid in lot.history():
        history.append({'bidder_username': bid.bidder.username,
                        'bid_amount': money_format(bid.bid_amount, request.shop),
                        'bid_time': date(bid.bid_time, 'r'),
                        }) 

    t = loader.get_template('bidding/blocks/view_history_lot_description.html')
    c = RequestContext(request, {'lot': lot, 'form': form})
    block_description = (t.render(c))
    image = lot.image()
    lot_dic = {'count_bidders': lot.count_bidders(),
               'count_bids': lot.count_bids(),
               'time_left_long': lot.time_left_long(),
               'title': lot.title,
               'dir_back': reverse('bidding_view_lot', args=[lot.id]),
               'image': {'original': image.image.url if image else None,
                         'small': image.image.url_100x100 if image else None,
                         'medium': image.image.url_400x400 if image else None,
                        }
             } 

    return HttpResponse(my_render(request, {
                                         'history': history,
                                         'description': block_description,
                                         'page_title': lot.title,
                                         'page_description': '%s, %s' % (lot.title, striptags(lot.description)),
                                         'lot': lot_dic, 
                                        }, 'view_history_lot'))


@shop_required
def bidding_view_item(request, id):
    #TODO: filter by state lot
    #TODO: add csrf_token to form
    item = get_object_or_404(Item, pk=id)

    request.shop.add_view()

    t = loader.get_template('bidding/blocks/view_item_form.html')
    c = RequestContext(request, {'item': item})
    block_view_item_form = (t.render(c))

    images = []
    for img in item.imageitem_set.all():
        images.append({'original': img.image.url if img else None,
                       'small': img.image.url_100x100 if img else None,
                       'medium': img.image.url_400x400 if img else None,
                       })
    
    param = {
        'item': 
                {'title': item.title,
                 'category': item.category.name,
                 'subcategory': item.subcategory.name if item.subcategory else "",
                 'title': item.title, 
                 'description': item.description, 
                 },
        'user_is_logged': request.user.is_authenticated() and not request.shop.is_admin(request.user),
        'form': block_view_item_form, 
        'images': images, 
        'page_title': item.title,
        'page_description': '%s, %s' % (item.title, striptags(item.description)) 
    }
    
    return HttpResponse(my_render(request, param, 'view_item'))


@shop_required
def bidding_buy_now(request, id):
    #TODO: filter by state lot
    #TODO: add csrf_token to form
    
    item = get_object_or_404(Item, pk=id)
    
    if not (item.shop == request.shop):
        raise Http404
        
    if (not request.user.is_authenticated()) or request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(settings.LOGIN_URL+"?next="+request.get_full_path())

    cart = request.cart
    cart.add(item, item.price, 1)
        
    request.flash['message'] = unicode(_("Product added to your cart"))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('my_shopping'))
    

def bidding_map(request, id):
    about = get_object_or_404(About, pk=id)
    return render_to_response('bidding/map.html', 
                              {'about': about},
                              RequestContext(request))
    
@shop_required
def bidding_search(request):
    """
    """
    query = ''
    form = BiddingSearchForm(shop=request.shop, data=request.GET)
    
    if form.is_valid():
        query = form.get_query()
        results = form.search()
    else:
        results = form.all_results()
    
    pager = Paginator(results, PAGE_SEARCH)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1        
    try:
        products = pager.page(page)
    except (EmptyPage, InvalidPage):
        products = pager.page(pager.num_pages)
    paged = (pager.num_pages > 1)
    
    t = loader.get_template('bidding/blocks/search.html')
    c = RequestContext(request, {'form': form, 
                                 'products' : products,
                                 'pages': pager.page_range,
                                 'paged': paged })
    block_search = (t.render(c))
    getvars = "&q=%s" % form.cleaned_data.get("q")
    
    t = loader.get_template('paginator.html')
    filter_params = {'q': form.cleaned_data.get("q", '')}
    c = RequestContext(request, {'objects': products, 
                                 'getvars': getvars,
                                 'filter_params': filter_params,
                                 'pages': pager.page_range,
                                 'paged': paged})
    
    paginator = (t.render(c))
    
    try:
        page = DynamicPageContent.objects.filter(shop=request.shop, page="search").get()
        description = striptags(page.meta_content)
    except DynamicPageContent.DoesNotExist:
        description = "No meta description found"
        
    return HttpResponse(my_render(request, {'results': block_search,
                                            'paginator': paginator,
                                            'page_title': 'Search',
                                            'page_description': description 
                                            }, 'search'))


@shop_required    
def pages(request, name_page):
    page = get_object_or_404(Page, shop = request.shop, name_link = name_page)
    param = {
        'page': {'title': page.title, 'body': page.body},
        'page_title': page.title,
        'page_description': '%s' % striptags(page.meta_content)
    }
    return HttpResponse(my_render(request, param, 'page'))
    

@shop_required    
def pages_sitemap(request):
    urls = ""
    for page in Page.objects.filter(shop = request.shop):
        urls += """<url><loc>%(url)s</loc><lastmod>%(last_mod)s</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>""" % {
            'url': request.build_absolute_uri(page.get_bidding_url()),
            'last_mod': page.last_updated.strftime("%Y-%m-%d")
        }

    try:
        about = About.objects.get(shop = request.shop)
        urls += """<url><loc>%(url)s</loc><lastmod>%(last_mod)s</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>""" % {
            'url': request.build_absolute_uri(reverse("bidding_about_us")),
            'last_mod': about.last_updated.strftime("%Y-%m-%d")
        }
    except About.DoesNotExist:
        pass
    
    try:
        home = Home.objects.get(shop = request.shop)
        urls += """<url><loc>%(url)s</loc><lastmod>%(last_mod)s</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>""" % {
            'url': request.build_absolute_uri(reverse("bidding_home")),
            'last_mod': home.last_updated.strftime("%Y-%m-%d")
        }
    except Home.DoesNotExist:
        pass
       
    sitemap = """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%(urls)s</urlset>""" % {'urls': urls}
    return HttpResponse(sitemap)
