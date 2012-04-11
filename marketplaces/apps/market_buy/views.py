import logging
import datetime
import bisect

from django.conf import settings
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from auth.decorators import login_required
from django.core.mail.message import EmailMultiAlternatives
from uni_form.helpers import FormHelper, Layout, Fieldset, Row, Submit

from market_buy.forms import AdvancedSearchForm


def advanced_search(request, reset=False):
    marketplace = request.marketplace

    if reset:
        form = AdvancedSearchForm(marketplace=marketplace)
    else:
        form = AdvancedSearchForm(marketplace=marketplace, data=request.GET)


    if request.GET.get("do"):

        result_list = []
        if form.is_valid():
    
            result_list = form.search()
            
            pager = Paginator(result_list, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)

            try:
                page = int(request.GET.get("page", "1"))
            except:
                page = 1

            try:
                paginator = pager.page(page)
            except (EmptyPage, InvalidPage):
                raise Http404

            paged = (pager.num_pages > 1)

            return render_to_response(
                "%s/buy/advanced_search_results.html" % marketplace.template_prefix, 
                {"result_list": paginator, "form": form,  
                 "pages": pager.page_range, "paged": paged, "total": pager.count, 
                 "view_mode": form.cleaned_data["view_by"]}, RequestContext(request))

    form_helper = FormHelper()
    layout = Layout(
        Fieldset("", "q"),
        Fieldset("", Row("categories", "subcategories")),
        Fieldset("", "include"),
        Fieldset("", Row("from_price", "to_price")),
        Fieldset("", "sort"),
        Fieldset("", "view_by"),
    )
    form_helper.add_layout(layout)
    submit = Submit("do", _("Search"))
    submit.field_classes = "button_primary"
    form_helper.add_input(submit)

    return render_to_response(
        "%s/buy/advanced_search.html" % marketplace.template_prefix, 
        {"form": form, "helper": form_helper} , RequestContext(request))


def categories(request):
    """ Return the categories for an specifica marketplace """
    return render_to_response("%s/buy/categories.html" % request.marketplace.template_prefix, 
                              {} , RequestContext(request))

def howtobuy(request):
    """ Return the how to buy for an specific marketplace """
    return render_to_response("%s/buy/howtobuy.html" % request.marketplace.template_prefix, 
                              {} , RequestContext(request))
def editor_pick(request):
    """ Return a list of items marked as favorites by admins  """
    from models import EditorPick
    
    marketplace = request.marketplace
    picks = EditorPick.get_available_picks(marketplace)
    return render_to_response("%s/buy/favorites.html" % request.marketplace.template_prefix, 
                              {'picks' : picks} , RequestContext(request))


def latest_items(request):
    """ Return the list of the latest 20(?) posted items in the stores """
    from inventory.models import Product
    marketplace = request.marketplace
    
    latest_items = Product.objects.filter(shop__marketplace=marketplace, latest_item=True, has_image=True)[:10]
    
    return render_to_response("%s/buy/latest_items.html" % request.marketplace.template_prefix, 
                              {'latest_items' : latest_items} , RequestContext(request))

def map_pick(request):
    """ Return """
    from shops.models import Shop
    marketplace = request.marketplace
    shops = Shop.actives.filter(marketplace=marketplace)
    return render_to_response("%s/buy/map_pick.html" % request.marketplace.template_prefix, 
                              {'shops' : shops} , RequestContext(request))

def show_listing(request):
    """ Return the list of shows added by admins """
    
    from market_buy.models import Show
    marketplace = request.marketplace
    shows = Show.objects.filter(marketplace=marketplace).filter(date_to__gte=datetime.datetime.today())
    
    params = {'states': STATE_CHOICES, 'shows': shows }
    
    return render_to_response("%s/buy/show_listing.html" % request.marketplace.template_prefix, 
                              params , RequestContext(request))

def show_search(request):
    """ Shows search """
    from geopy import geocoders
    from distance_helper import distance_between_points
    from market_buy.models import Show
    marketplace = request.marketplace
    
    city = request.POST.get('city', None)
    state = request.POST.get('state')
    zip = request.POST.get('zip')
    country = request.POST.get('country', 'US')
        
    if (city == u'') or (state == u''):
        request.flash['message'] = "Please, fill at least the city and state fields to complete the search!"
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse("buy_show_listing"))
    
    try:
        g = geocoders.Google(settings.GOOGLE_KEY)
        place = "%s, %s, %s" % (city, state, country)
        place, point1 = g.geocode(place)
    except Exception, e:
        request.flash['message'] = "Could not determine your location. Try again with other input data!"
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse("buy_show_listing"))
        
    all_shows = Show.objects.filter(marketplace=marketplace).filter(date_to__gte=datetime.datetime.today())
    
    max_distance = 1500
    metric = "miles"
    
    shows = []
    
    for show in all_shows:
        point2 = [float(x) for x in show.geo_location()]
        distance = distance_between_points(point1, point2 , metric)
        if distance < max_distance:
            bisect.insort(shows, (int(distance), show))

    params = {'states': STATE_CHOICES, 'shows': shows, 'place': place}
    
    return render_to_response("%s/buy/show_listing.html" % request.marketplace.template_prefix, 
                              params, RequestContext(request))
    
def shop_local(request):
    """ Return the shops near some location """
    
    
    from shops.models import Shop
    from geopy import geocoders
    from distance_helper import distance_between_points
    
    in_range = []
    params = {}
    params['states'] = STATE_CHOICES
    
    if request.method == "POST":
        max_distance = float(request.POST.get("max_distance"))
        metric = request.POST.get("metric", "miles")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country", "US")
        
        try:
            g = geocoders.Google(settings.GOOGLE_KEY)
            place = "%s, %s, %s" % (city, state, country)
            place, point1 = g.geocode(place)
        except Exception, e:
            logging.critical(e)
            request.flash['message'] = "Invalid input!"
            request.flash['severity'] = "error"
            return render_to_response("%s/buy/shop_local.html" % request.marketplace.template_prefix, 
                              {'shops' : in_range} , 
                              RequestContext(request))
        
        marketplace = request.marketplace
        shops = Shop.actives.filter(marketplace=marketplace)
        
        for shop in shops:
            point2 = [float(x) for x in shop.geo_location()]
            distance = distance_between_points(point1, point2 , metric)
            logging.critical("%s - %s - %s" % (shop, point2, distance))
            if distance < max_distance:
                bisect.insort(in_range, (int(distance), shop))
        
        params.update({'shops': in_range, 'metric' : metric, 'selected_city': city, 'selected_state': state, 'do_search': True})
    
    else:
        params.update({'shops': [], 'do_search': False})
    
    return render_to_response("%s/buy/shop_local.html" % request.marketplace.template_prefix, 
                              params , 
                              RequestContext(request))


def top_sellers(request):
    """ Return top seller of the month, and the last 10 top sellers """
    from shops.models import Shop
    from market_buy.models import BestSeller
    
    marketplace = request.marketplace
    sellers = BestSeller.objects.filter(shop__marketplace=marketplace).order_by("-to_date")[:10]
    
    if not sellers:
        delta = 7
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(delta)
    
        best_seller = BestSeller()
        best_seller.shop = Shop.objects.all().filter(marketplace=marketplace).order_by('?')[0]
        best_seller.from_date = date_from
        best_seller.to_date = date_to
        best_seller.revenue = 0
        best_seller.save()
        sellers = BestSeller.objects.filter(shop__marketplace=marketplace).order_by("-to_date")
    
    return render_to_response("%s/buy/top_sellers.html" % request.marketplace.template_prefix, 
                              {'best_sellers' : sellers} , RequestContext(request))


def wish_list(request):
    """ Return the wishes list posted by the users """
    from market_buy.models import WishListItem
    from market_buy.forms import WishListItemForm
    
    marketplace = request.marketplace
    wihs_list = WishListItem.objects.filter(marketplace=marketplace).order_by("posted_on")    
    form = WishListItemForm()
    
    return render_to_response("%s/buy/wish_list.html" % request.marketplace.template_prefix, 
                              {
                               'wish_list' : wihs_list,
                               'form' : form,
                               } , 
                              RequestContext(request))


def ajax_get_subcategories(request):
    from market.models import MarketSubCategory, MarketCategory
    categories = request.REQUEST.get('categories', "")
    try:
        categories = categories.split(",")
        logging.info("categories: %s" % categories)
        categories = MarketCategory.objects.filter(id__in=categories)
        logging.info("categories: %s" % categories)
        sub_categories = MarketSubCategory.objects.filter(parent__in=categories).order_by("name")
        html = ""
        for sub in sub_categories:
            html += '<option value="%d">%s</option>' % (sub.id, sub.name)
        logging.info("subscategories: %s" % html)
        return HttpResponse(html)
    except:
        logging.exception("error getting subcategories")
        return HttpResponse("")
    
@login_required
def post_wish_list_item(request):
    from market_buy.forms import WishListItemForm
    
    user = request.user
    marketplace = request.marketplace
    if request.method == "POST":
        form = WishListItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit = False)
            item.posted_by = user
            item.marketplace = marketplace
            item.save()
            request.flash['message'] = _("Item was successfully added...")
            request.flash['severity'] = "success"
           
        else:
            request.flash['message'] = _("Item could not be added...")
            request.flash['severity'] = "error" 
        
    return HttpResponseRedirect(reverse("buy_wish_list"))


def item_redirect(request, id):
    #from inventory.models import Product
    from for_sale.models import Item
    
    product = get_object_or_404(Item, id=id)
    
    host_name = product.shop.default_dns
    #if hasattr(product, 'item'): 
    path = reverse("bidding_view_item", urlconf="stores.urls", args=[product.id])
    return HttpResponseRedirect("http://%s%s" % (host_name, path))
    #else:
    #    return HttpResponseRedirect("/")


    
def product_redirect(request, id):
    from inventory.models import Product
    
    product = get_object_or_404(Product, id=id)
    
    host_name = product.shop.default_dns
    if hasattr(product, 'item'): 
        path = reverse("bidding_view_item", urlconf="stores.urls", args=[product.id])
        return HttpResponseRedirect("http://%s%s" % (host_name, path))
    elif hasattr(product, 'lot'):
        path = reverse("bidding_view_lot", urlconf="stores.urls", args=[product.id])
        return HttpResponseRedirect("http://%s%s" % (host_name, path))
    else:
        return HttpResponseRedirect("/")


@transaction.commit_on_success
def signup(request):
    from auth.models import User
    from auth import load_backend, login
    from users.models import Profile, EmailVerify
    from market_buy.forms import BuyerForm
    
    form = BuyerForm(request.POST or None)
    if form.is_valid():
        """ Generate Auth User """
        user = User.objects.create_user(form.cleaned_data["username"],
                                        form.cleaned_data["email"], 
                                        form.cleaned_data["password1"])
        
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.is_active = False
        user.save()
        
        """ Set profile """
        profile = Profile(user=user)
        profile.save()

        """ Send mail to confirm account """
        email_verify = EmailVerify(user=user, user_activation=True)
        code = email_verify.generate_code()
        email_verify.save()
        
        # TODO: remove this
        send_mail_account_confirmation(user, email_verify.code, request.marketplace)        
        
#        return HttpResponseRedirect(reverse('confirmemail', args=[code]))
#        for backend in settings.AUTHENTICATION_BACKENDS:
#            if user == load_backend(backend).get_user(user.pk):
#                user.backend = backend
#                break
#        if hasattr(user, 'backend'):
#            login(request, user)
        
        if request.session.get('sell_signup',False):
            request.flash['message'] = _("<h5>Please check your email and confirm your account to start selling...</h5>")
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('market_sell_signup'))
        else:
            request.flash['message'] = _("<h5>Please check your email and confirm your account. Once confirmed you can Buy or Sell on GreatCoins.com</h5>")
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('market_home'))
    else:
        #request.method == GET
        if request.GET.has_key('sell_signup'):
            request.session['sell_signup'] = request.GET.get('sell_signup','') == '1'

    return render_to_response('%s/buy/register.html'% request.marketplace.template_prefix, 
                              {'form': form},
                              RequestContext(request))


def login(request):
    from auth import authenticate, login
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next = request.POST.get('next', reverse("market_home"))
                return HttpResponseRedirect(next)
            else:
                request.flash['message'] = _("Your account is inactive... You must confirm your account before login.")
                request.flash['severity'] = "error"
        else:
            request.flash['message'] = _("You entered an invalid username or password. Please try again")
            request.flash['severity'] = "error"
            
        return render_to_response('%s/buy/login.html'% request.marketplace.template_prefix, 
                                  {'next': request.POST.get('next', None)},
                                  RequestContext(request))
    
    return render_to_response('%s/buy/login.html'% request.marketplace.template_prefix, 
                              {'next': request.GET.get('next', None)},
                              RequestContext(request))
    
def send_mail_account_confirmation(user, code, marketplace):
    """
        Send message to the user to confirm your account
    """
    link = "http://www.%s/buy/confirmemail/%s/" % (marketplace.base_domain , code)
    
    subject = "%s Account Confirmation" % marketplace.name    
    
    text_content = _("""
    Hi %(username)s,
    
    You recently registered at %(marketplace_name)s. Please confirm your account by following this link: %(link)s
                       
    Thanks.
                       
    %(marketplace_name)s Team.""") % {'username': user.username, 'link': link, 'marketplace_name': marketplace.name}
    
    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_FROM,
                                 [user.email, settings.EMAIL_FROM],
                                 headers={'X-SMTPAPI': '{\"category\": \"Account Confirmation\"}'})
    logging.critical(text_content);
    
    try:
        msg.send()
    except:
        logging.exception("failure sending mail")

def confirmemail(request, code):
    from users.models import EmailVerify
    marketplace = request.marketplace
    try:
        verify = EmailVerify.objects.filter(code = code).get()
        if not verify.user_activation:
            request.flash['message'] = _("<h5>Account verification failed</h5>")
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('market_home'))
            
        else:
            user = verify.user
            user.is_active = True
            user.save()
            
            if verify.verified:
                request.flash['message'] = _("<h5>Your account was already verified! You can login now <a href='%s'>here</a></h5>" % reverse("market_buy_login"))
                request.flash['severity'] = "success"
                return HttpResponseRedirect(reverse('market_home'))
            
            else:
                verify.verified = True
                verify.save()
            
            from auth import load_backend, login
            if not hasattr(user, 'backend'):
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.pk):
                        user.backend = backend
                        break
            if hasattr(user, 'backend'):
                login(request, user)
            
            params = {}
            
            return render_to_response(
                "%s/email_confirmed.html" % marketplace.template_prefix, params, RequestContext(request))
        
    except EmailVerify.DoesNotExist:
        request.flash['message'] = _("<h5>Account verification failed</h5>")
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('market_home'))

@login_required
def user_profile(request):
    from auth.models import User
    from users.forms import UserProfile
    from users.models import check_profile
    marketplace = request.marketplace
    user = request.user
    
    check_profile(User, instance=request.user)
    
    if request.method == 'POST':
        form = UserProfile(data=request.POST, user=user)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.street_address = form.cleaned_data['street_address']
            user.profile.city = form.cleaned_data['city']
            user.profile.state = form.cleaned_data['state']
            user.profile.zip = form.cleaned_data['zip']
            user.profile.country = form.cleaned_data['country']
            user.profile.phone = form.cleaned_data['phone']

            try:
                photo = request.FILES['photo']
                user.profile.photo = photo
            except:
                pass 

            user.save()
            user.profile.save()
        
            return HttpResponseRedirect(reverse('market_home'))
    else:
        initial = { 'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'street_address': user.profile.street_address,
                    'city': user.profile.city,
                    'state': user.profile.state,
                    'zip': user.profile.zip,
                    'country': user.profile.country,
                    'phone': user.profile.phone,
                    }
        form = UserProfile(initial=initial, user=user)
    
    params = {'form': form, 'photo': user.profile.photo }
    return render_to_response("%s/buy/profile.html" % marketplace.template_prefix,
                               params,
                               RequestContext(request))

@login_required
def delete_profile_image(request):
    from users.models import Profile
    try:
        profile = Profile.objects.get(user__id=request.user.id)
        profile.photo = ''
        profile.save()
    except Exception, ex:
        logging.debug(str(ex))

    return HttpResponseRedirect(reverse('market_buy_user_profile'))
