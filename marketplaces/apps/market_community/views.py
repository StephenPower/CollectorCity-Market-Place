# Create your views here.
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from auth.models import User
from shops.models import Shop 
from payments.gateways.braintreegw import BraintreeGateway 
from users.models import Profile 
from shops.forms import MailingListMemberForm


def profiles_list(request, letter):
    from shops.models import Shop
    
    marketplace = request.marketplace
    shops = Shop.objects.filter(marketplace=marketplace).filter(Q(name__startswith=letter.lower()) | Q(name__startswith=letter.upper()))
    return render_to_response("%s/community/profiles_list.html" % request.marketplace.template_prefix, 
                              {'shops':shops},
                              RequestContext(request))
                              
def profiles(request):
    from shops.models import Shop
    
    letters =[]
    shops = Shop.objects.all()
    for shop in shops: letters.append(shop.name[0])  
    
    letters = set(letters)
    return render_to_response("%s/community/profiles.html" % request.marketplace.template_prefix, {'letters' : letters}, RequestContext(request))


def forums(request):
    return render_to_response("%s/community/forums.html" % request.marketplace.template_prefix, 
                              {},
                              RequestContext(request))

def blogs(request):
    import datetime
    from blog_pages.models import Post
    from models import PostEditorPick
    
    today = datetime.date.today()
    wday = today.weekday()
    monday = today - datetime.timedelta(days=wday)
    sunday = monday + datetime.timedelta(days=6)
    
    marketplace = request.marketplace
    last_posts = Post.objects.filter(shop__marketplace=marketplace).order_by("-date_time")[:5]
    posts_picks = PostEditorPick.objects.filter(marketplace=marketplace).order_by("order")
    most_visited = Post.objects.filter(shop__marketplace=marketplace)
    most_visited = most_visited.filter(date_time__range=(monday, sunday)).order_by("-views")[:5]
    
    return render_to_response("%s/community/blogs.html" % request.marketplace.template_prefix, 
                              {
                               'last_posts' : last_posts,
                               'posts_picks' : posts_picks,
                               'most_visited' : most_visited,
                              },
                              RequestContext(request))
    
def faq(request):
    from market_community.models import FAQCategory
    marketplace = request.marketplace
    
    categories = FAQCategory.objects.filter(marketplace=marketplace)
    return render_to_response("%s/community/faq.html" % request.marketplace.template_prefix, 
                              {'categories': categories},
                              RequestContext(request))

def overview(request):
    from blog_pages.models import Post
    from shops.models import Shop
    from market_community.models import MarketPlaceAnnouncement
    from market.forms import MarketMailingListMemberForm
    
    marketplace = request.marketplace
    announcements = MarketPlaceAnnouncement.objects.filter(marketplace=marketplace).order_by("-posted_on")[:5]
    shops = Shop.objects.filter(marketplace=marketplace).order_by("-date_time")[:3]
    last_posts = Post.objects.filter(shop__marketplace=marketplace).order_by("-date_time")[:5]


    if request.method == "POST":
        form = MarketMailingListMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.marketplace = request.marketplace
            member.save()
            request.flash['message'] = unicode(_("Email successfully registered."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse("market_community"))
    else:
        form = MailingListMemberForm()   
    
    return render_to_response("%s/community/overview.html" % request.marketplace.template_prefix, 
                              {
                               'announcements' : announcements,
                               'last_posts' : last_posts,
                               'shops' : shops,
                               'mailing_list_form' : form,
                              },
                              RequestContext(request))
