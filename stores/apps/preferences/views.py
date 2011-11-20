"""
    Edit shop preferences
"""
import datetime
from preferences.forms import MarketingForm, TaxStateEditForm
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from auth.forms import PasswordChangeForm
from core.decorators import shop_admin_required

from forms import GeneralPreferenceForm, TaxesPreferenceForm, AuctionsPreferenceForm
from forms import ShippingWeightForm, ShippingPriceForm, ShippingItemForm, TaxStateForm, DnsShopForm, EmailNotificationForm, ShopPoliciesForm
from forms import UsernameChangeForm, ProfileForm
from models import Preference, ShippingWeight, ShippingPrice, ShippingItem, TaxState, DnsShop, EmailNotification, ShopPolicies
from models import TYPE_NOTIFICATION


@shop_admin_required
def preferences_general(request):
    shop = request.shop
    profile = shop.admin.get_profile()
    preferences = Preference.get_preference(shop)
    form = GeneralPreferenceForm(request.POST or None, instance=preferences)
    profile_form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid() and profile_form.is_valid():
        preferences = form.save(commit = False)
        preferences.shop = shop
        preferences.save()
        
        profile = profile_form.save(commit = True)
        shop.update_geolocation()
    
        request.flash['message'] = unicode(_("General preferences successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('preferences_general'))
    
    return render_to_response('preferences/preferences_general.html', 
                              {'form': form, 'profile_form': profile_form}, 
                              RequestContext(request))   

@shop_admin_required
def add_state_tax(request):
    shop = request.shop
    
    
    if request.method == 'POST':
        form_tax = TaxStateForm(shop, request.POST)
        if form_tax.is_valid():
            
            tax = form_tax.save(commit = False)
            tax.shop = shop
            tax.save()
            request.flash['message'] = unicode(_("Tax successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_taxes'))
    else:
        form_tax = TaxStateForm(shop)    
        
    return render_to_response('preferences/preferences_add_state_tax.html', 
                              {'form_tax': form_tax },
                              RequestContext(request))

@shop_admin_required
def edit_tax(request, id):
    
    shop = request.shop
    tax = get_object_or_404(TaxState, pk=id)
        
    if request.method == 'POST':
        form_tax = TaxStateEditForm(shop, request.POST, instance=tax)
        if form_tax.is_valid():
            tax = form_tax.save(commit = True)
            request.flash['message'] = unicode(_("Tax successfully updated."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_taxes'))
    else:
        form_tax = TaxStateEditForm(shop, instance=tax)
        
    return render_to_response('preferences/preferences_edit_tax.html', 
                              {'form_tax': form_tax },
                              RequestContext(request))

        
@shop_admin_required    
def preferences_taxes(request):
    shop = request.shop
    taxs = TaxState.objects.filter(shop=shop).order_by("state")
    form_tax = TaxStateForm(shop)
    
    return render_to_response('preferences/preferences_taxes.html', 
                              {'form_tax': form_tax, 'taxs': taxs}, 
                              RequestContext(request))   

@shop_admin_required
def delete_tax(request, id):
    tax = get_object_or_404(TaxState, pk=id)
    shop = request.shop
    if tax.shop != shop:
        raise Http404
    tax.delete()
    return HttpResponseRedirect(reverse('preferences_taxes'))


@shop_admin_required
def save_googlecheckout_settings(request):
    from payments.models import GoogleCheckoutShopSettings
    from payments.forms import GoogleCheckoutShopSettingsForm
    
    shop = request.shop
    
    try:
        current_google_settings = GoogleCheckoutShopSettings.objects.filter(shop=shop)[0]
    except IndexError:
        current_google_settings = None
    
    if request.method == "POST":
        google_form = GoogleCheckoutShopSettingsForm(request.POST, instance=current_google_settings)
        if google_form.is_valid():
            googlesettings = google_form.save(commit = False)
            googlesettings.shop = shop        
            googlesettings.save()
            request.flash['message'] = unicode(_("Google checkout settings successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_payment_google_checkout'))
        else:
            request.flash['message'] = unicode(_("Could not save Google checkout settings!"))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('preferences_payment_google_checkout'))
    else:
        return preferences_payment_google_checkout(request)
    

@shop_admin_required
def save_braintree_settings(request):
    from payments.models import BraintreeShopSettings
    from payments.forms import BraintreeShopSettingsForm
    
    shop = request.shop
    
    try:
        current_bt_settings = BraintreeShopSettings.objects.filter(shop=shop)[0]
    except IndexError:
        current_bt_settings = None
    
    if request.method == "POST":
        braintree_form = BraintreeShopSettingsForm(request.POST, instance=current_bt_settings)
        if braintree_form.is_valid():
            braintreesettings = braintree_form.save(commit = False)
            braintreesettings.shop = shop        
            braintreesettings.save()
            request.flash['message'] = unicode(_("Braintreee settings successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_payment_credit_cards'))
        else:
            request.flash['message'] = unicode(_("Could not save Braintree settings!"))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('preferences_payment_credit_cards'))
    else:
        return preferences_payment_credit_cards(request)


@shop_admin_required
def delete_googlecheckout_settings(request, setting_id):
    from payments.models import GoogleCheckoutShopSettings
    setting = get_object_or_404(GoogleCheckoutShopSettings, pk=setting_id)
    
    shop = request.shop
    if setting.shop != shop:
        raise Http404
    
    setting.delete()
    
    request.flash['message'] = unicode(_("Google Checkout settings successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('preferences_payment_google_checkout'))

@shop_admin_required
def delete_braintree_settings(request, setting_id):
    from payments.models import BraintreeShopSettings
    setting = get_object_or_404(BraintreeShopSettings, pk=setting_id)
    
    shop = request.shop
    if setting.shop != shop:
        raise Http404
    
    setting.delete()
    
    request.flash['message'] = unicode(_("Braintree settings successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('preferences_payment_credit_cards'))

@shop_admin_required
def save_manual_payment(request):
    from payments.models import ManualPaymentShopSettings
    from payments.forms import ManualPaymentShopSettingsForm
    
    shop = request.shop
    
    if request.method == "POST":
        manual_payment_form = ManualPaymentShopSettingsForm(shop, request.POST)
        if manual_payment_form.is_valid():
            manual_payment = manual_payment_form.save(commit = False)
            manual_payment.shop = shop        
            manual_payment.save()
            request.flash['message'] = unicode(_("Manual payment successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_payment_manual'))
        else:
            errors = ",".join(manual_payment_form.errors)
            request.flash['message'] = unicode(_("Could not save Manual payment! fields with errors: %s" % errors))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('preferences_payment_manual'))
    else:
        return preferences_payment_manual(request)


@shop_admin_required
def delete_manual_payment(request, payment_id):
    from payments.models import ManualPaymentShopSettings
    manual_payment = get_object_or_404(ManualPaymentShopSettings, pk=payment_id)
    
    shop = request.shop
    if manual_payment.shop != shop:
        raise Http404
    
    manual_payment.delete()
    
    request.flash['message'] = unicode(_("Manual Payment successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('preferences_payment_manual'))
    

@shop_admin_required
def edit_manual_payment(request, payment_id):
    from payments.forms import ManualPaymentShopSettingsForm
    from payments.models import ManualPaymentShopSettings
    
    manual_payment = get_object_or_404(ManualPaymentShopSettings, pk=payment_id)
    
    shop = request.shop
    if manual_payment.shop != shop:
        raise Http404
    
    if request.method == "POST":
        form = ManualPaymentShopSettingsForm(shop, request.POST, instance=manual_payment)    
        if form.is_valid():
            method = form.save(commit=True)
            request.flash["message"] = _("Manual payment successfully edited")
            request.flash["severity"] = "success"
            return HttpResponseRedirect(reverse("preferences_payment_manual"))
        
    form = ManualPaymentShopSettingsForm(shop, instance=manual_payment)
        
    return render_to_response('preferences/preferences_payment_manual_edit.html', 
                              { 
                               'form' : form,
                              }, 
                              RequestContext(request))

@shop_admin_required
def preferences_payments(request):
    shop = request.shop
    limit = shop.plan().payment_methods
#    current = 0
#    if shop.get_features().paypal: current += 1
#    if shop.get_features().credit_card: current += 1
#    if shop.get_features().google_checkout: current += 1
#    if shop.get_features().manual_payment: current += 1
#    params = {'available_methods' : limit, 'current_methods': current }
    params = {}
    return render_to_response("preferences/preferences_payments.html", params, RequestContext(request))
  
@shop_admin_required    
def preferences_payment_paypal(request):
    from payments.models import PayPalShopSettings
    
    shop = request.shop
    
    if not shop.paypal_feature_enabled():
        raise Http404
    
    try:
        paypal_settings = PayPalShopSettings.objects.filter(shop=shop)[0]
    except IndexError:
        paypal_settings = None
    
    return render_to_response('preferences/preferences_payment_paypal.html', 
                              { 
                               'paypal_settings': paypal_settings,
                              }, 
                              RequestContext(request))


@shop_admin_required    
def preferences_payment_credit_cards(request):
    from payments.forms import BraintreeShopSettingsForm
    from payments.models import BraintreeShopSettings
    
    shop = request.shop
    
    if not shop.credit_card_feature_enabled():
        raise Http404
    
    try:
        current_braintree_settings = BraintreeShopSettings.objects.filter(shop=shop)[0]
    except IndexError:
        current_braintree_settings = None
    
    braintree_form = BraintreeShopSettingsForm(instance=current_braintree_settings)
    
    return render_to_response('preferences/preferences_payment_credit_cards.html', 
                              { 
                               'braintree_form' : braintree_form,
                               'braintree_settings' : current_braintree_settings,
                              }, 
                              RequestContext(request))


@shop_admin_required
def preferences_payment_google_checkout(request):
    from payments.forms import GoogleCheckoutShopSettingsForm
    from payments.models import GoogleCheckoutShopSettings
    
    shop = request.shop
    
    if not shop.google_checkout_feature_enabled():
        raise Http404
    
    try:
        current_google_settings = GoogleCheckoutShopSettings.objects.filter(shop=shop)[0]
    except IndexError:
        current_google_settings = None
        
    google_form = GoogleCheckoutShopSettingsForm(instance=current_google_settings)
        
    return render_to_response('preferences/preferences_payment_google_checkout.html', 
                              { 
                               'google_form': google_form,
                               'google_settings' : current_google_settings,
                              }, 
                              RequestContext(request))


@shop_admin_required    
def preferences_payment_manual(request):
    from payments.forms import ManualPaymentShopSettingsForm
    from payments.models import ManualPaymentShopSettings
    
    shop = request.shop
    
    if not shop.manual_payment_feature_enabled():
        raise Http404
    
    manual_payment_form = ManualPaymentShopSettingsForm(shop)
    manual_payments = ManualPaymentShopSettings.objects.filter(shop=shop)
    
    return render_to_response('preferences/preferences_payment_manual.html', 
                              { 
                               'manual_payment_form' : manual_payment_form,
                               'manual_payments' : manual_payments,
                              }, 
                              RequestContext(request))


@shop_admin_required 
def payment_paypal_setpermissions(request):
    
    from payments.gateways.paypal import PayPalGateway
    
    ppgw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                         password=settings.PAYPAL_PASSWORD,
                         sign=settings.PAYPAL_SIGNATURE,
                         debug=settings.PAYPAL_DEBUG)
    required_perms = [
        "Email", 
        "Name",
        "RefundTransaction",
        "SetExpressCheckout", 
        "GetExpressCheckoutDetails",        
        "DoExpressCheckoutPayment",
        "DoAuthorization",
        "DoCapture",
        "DoReauthorization"
    ]
    
    success, response = ppgw.SetAccessPermissions(return_url=request.build_absolute_uri(reverse("preferences_payment_paypal_return", args=["agree"])), 
                                                  cancel_url=request.build_absolute_uri(reverse("preferences_payment_paypal_return", args=["cancel"])), 
                                                  logout_url=request.build_absolute_uri(reverse("preferences_payment_paypal_return", args=["logout"])), 
                                                  required_permissions=required_perms)
    
    if success:
        return HttpResponseRedirect(ppgw.redirect_url(cmd='_access-permission-login', token=response['TOKEN'][0]))
    else:
        logging.info(response)
        request.flash["message"] = _("Paypal not available, try again later")
        request.flash["severity"] = "notice"
        #return HttpResponseRedirect(reverse("preferences_general"))
        return HttpResponse("error")

@shop_admin_required    
def payment_paypal_disable(request):
    from payments.forms import PayPalShopSettingsForm, GoogleCheckoutShopSettingsForm
    from payments.models import PayPalShopSettings, GoogleCheckoutShopSettings
    
    shop = request.shop
    
    try:
        paypal_settings = PayPalShopSettings.objects.get(shop=shop)
    except PayPalShopSettings.DoesNotExist:
        paypal_settings = None
        request.flash["message"] = _("Paypal didn't seems to be enable")
        request.flash["severity"] = "error"
        return HttpResponseRedirect(reverse("preferences_payment_paypal"))

    #TODO: call update permissions    
    paypal_settings.delete()
    request.flash["message"] = _("Paypal disabled")
    request.flash["severity"] = "notice"
    return HttpResponseRedirect(reverse("preferences_payment_paypal"))

@shop_admin_required 
def payment_paypal_return(request, action):
    """
        Process the request of the shop admin coming back from paypal. 
    """
    from payments.gateways.paypal import PayPalGateway
    from payments.models import PayPalShopSettings
    if action == 'agree':
        ppgw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                         password=settings.PAYPAL_PASSWORD,
                         sign=settings.PAYPAL_SIGNATURE,
                         debug=settings.PAYPAL_DEBUG)
        success, response = ppgw.GetAccessPermissionDetails(request.GET['token'])
        
        if not success:
            request.flash['message'] = unicode(_("Preferences not saved. PayPal respond: %s" % response["L_SHORTMESSAGE0"][0]))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('preferences_payment_paypal'))
        
        perms = []
        for key in response.iterkeys():
            if 'L_ACCESSPERMISSIONSTATUS' not in key:
                continue
            if response[key][0] == 'Accepted':
                idx = key.split('L_ACCESSPERMISSIONSTATUS')[1]
                perms.append(response['L_ACCESSPERMISSIONNAME%s' % idx][0])
                
        try:
            paypalinst = PayPalShopSettings.objects.get(shop=request.shop)
        except PayPalShopSettings.DoesNotExist:
            paypalinst = PayPalShopSettings(shop=request.shop)
        
        paypalinst.payer_id = response['PAYERID'][0]
        paypalinst.email = response['EMAIL'][0]
        paypalinst.first_name = response['FIRSTNAME'][0] 
        paypalinst.last_name = response['LASTNAME'][0]
        paypalinst.perms = perms
        paypalinst.save()
        
        request.flash['message'] = unicode(_("Preferences successfully saved."))
        request.flash['severity'] = "success"

    if action == 'cancel':
        request.flash['message'] = unicode(_("You have decided not to complete the setup process. Your Paypal payment option is still disabled."))
        request.flash['severity'] = "error"
        
    if action == 'logout':
        request.flash['message'] = unicode(_("You are logged out from Paypal!"))
        request.flash['severity'] = "error"

    return HttpResponseRedirect(reverse('preferences_payment_paypal'))

@shop_admin_required
def preferences_auctions(request):
    shop = request.shop
    preferences = Preference.get_preference(shop)
    if request.method == 'POST':
        form = AuctionsPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.shop = shop
            request.flash['message'] = unicode(_("Auctions preferences successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_auctions'))
    else:            
        form = AuctionsPreferenceForm(instance=preferences)
    return render_to_response('preferences/preferences_auctions.html', 
                              {'form': form}, 
                              RequestContext(request))  


@shop_admin_required
def preferences_shipping(request):
    shop = request.shop

    shipping_weight = ShippingWeight.objects.filter(shop=shop)
    shipping_price = ShippingPrice.objects.filter(shop=shop)
    shipping_item = ShippingItem.objects.filter(shop=shop)

    form_weight = ShippingWeightForm()
    form_price = ShippingPriceForm()
    form_item = ShippingItemForm()
    
    if request.method == 'POST':
        if request.POST.get('type') == 'weight':
            form_weight = ShippingWeightForm(request.POST)
            form = form_weight 
        elif request.POST.get('type') == 'price':
            form_price = ShippingPriceForm(request.POST)
            form = form_price 
        elif request.POST.get('type') == 'item':
            form_item = ShippingItemForm(request.POST)
            form = form_item 
            
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.shop = shop
            shipping.save()
            request.flash['message'] = unicode(_("Flat rate shipping successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_shipping'))
            
    return render_to_response('preferences/preferences_shipping.html', 
                              {'shipping_weight': shipping_weight,
                               'shipping_price': shipping_price,
                               'shipping_item': shipping_item,
                               'form_weight': form_weight,
                               'form_price': form_price,
                               'form_item': form_item,
                               }, 
                              RequestContext(request))  

@shop_admin_required
def delete_shipping_weight(request, id):
    shipping_weight = get_object_or_404(ShippingWeight, pk=id)
    shop = request.shop
    if shipping_weight.shop != shop:
        raise Http404
    shipping_weight.delete()
    return HttpResponseRedirect(reverse('preferences_shipping'))
    
@shop_admin_required
def delete_shipping_price(request, id):
    shipping_price = get_object_or_404(ShippingPrice, pk=id)
    shop = request.shop
    if shipping_price.shop != shop:
        raise Http404
    shipping_price.delete()
    return HttpResponseRedirect(reverse('preferences_shipping'))
    
@shop_admin_required
def delete_shipping_item(request, id):
    shipping_item = get_object_or_404(ShippingItem, pk=id)
    shop = request.shop
    if shipping_item.shop != shop:
        raise Http404
    shipping_item.delete()
    return HttpResponseRedirect(reverse('preferences_shipping'))


@shop_admin_required
def preferences_email(request):
    type_notification = TYPE_NOTIFICATION
    return render_to_response('preferences/preferences_email.html', 
                              {'type_notification':type_notification,
                               }, 
                              RequestContext(request))  

@shop_admin_required
def ajax_edit_notification(request):
    #TODO: check this key in TYPE_NOTIFICATION
    try:
        shop = request.shop
        if request.method == 'POST':
            key = request.POST.get('key')
        else:
            key = request.GET.get('key')
        try:
            email_notification = EmailNotification.objects.filter(type_notification=key, shop=shop).get()
        except:
            if key == "NON":
                subject = "[{{shop}}]  {{ buyer_name }} place a new order"
                body = """
{{ buyer_name }} placed a new order with you today ({{ sell_date }}).

Paymenth Gateway: {{ gateway }}

Shipping address:
    {{ shipping_street_address }}
    {{ shipping_city }}, {{ shipping_state }} {{ shipping_zip }},  {{ shipping_country }}

Items:
{% for item in items %}
    {{ item.qty }}x {{ item.title }} | {{  item.total }}
{% endfor %}
                
Total Without Taxes: {{ sell_without_taxes }}
Total Taxes: {{ sell_total_taxes }}
Total Shipping: {{ sell_total_shipping }}
Total: {{ sell_total }} """
                
            elif key == "AWC":
                subject = "Congratulations {{ bidder_name }}!" 
                body = """
{{ bidder_name }}, you have won the {{ session_title }} on {{ shop }} that finished at {{ session_end }}

You bid u$s {{ bid_amount }} for the lot {{ lot_title }} on {{ bid_time }}.

Lot Description: {{ lot_description }}. """

            elif key == "OC":
                subject = "Order confirmation from {{ shop }}"
                body = body = """
Thank you for placing your order with {{ shop }}!

This email is to confirm your recent order.

Date: {{ sell_date }}
Shipping address:
    {{ shipping_street_address }}
    {{ shipping_city }}, {{ shipping_state }} {{ shipping_zip }},  {{ shipping_country }}

The order contains these items:
{% for item in items %}
   ** {{ item.qty }}x {{ item.title }}  | {{ item.total }}
{% endfor %}

Taxes     : {{ sell_total_taxes }}
Shipping  : {{ sell_total_shipping }}
Total     : {{ sell_total }}        """
            elif key == "CB":
                subject = "Contact from {{ shop }}"
                body = ""
                
            email_notification = EmailNotification(type_notification=key, shop=shop, subject=subject, body=body)
            
        form = EmailNotificationForm(request.POST or None, instance=email_notification)
        if form.is_valid():
            email_notification = form.save(commit=False)
            email_notification.type_notification = key
            email_notification.save()
            request.flash['message'] = unicode(_("Email notification successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_email'))
    
        return render_to_response('preferences/ajax_edit_notification.html',
                                  {'form': form, 
                                   'key': key,
                                   'email_notification': email_notification },
                                  RequestContext(request))
    except Exception, e:
        logging.critical(e)


@shop_admin_required
def preferences_policies(request):
    shop = request.shop
    
    try:
        policies = ShopPolicies.objects.filter(shop=shop).get()
    except ShopPolicies.DoesNotExist:
        policies = ShopPolicies(shop=shop)
        policies.save()
        
    if request.method == "POST":
        form = ShopPoliciesForm(request.POST)
        if form.is_valid():
            policies.refund_policy = form.cleaned_data['refund_policy']
            policies.terms_of_service = form.cleaned_data['terms_of_service']
            policies.privacy_policy = form.cleaned_data['privacy_policy']
            policies.save()
            request.flash['message'] = unicode(_("Policies successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('preferences_policies'))
        
        request.flash['message'] = unicode(_("Policies successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('preferences_policies'))
    
    
    form = ShopPoliciesForm(instance=policies)
    
    return render_to_response('preferences/preferences_policies.html', 
                              {'form': form}, 
                              RequestContext(request))  

@shop_admin_required
def preferences_dns(request):
    shop = request.shop
    dnss= DnsShop.objects.filter(shop=shop)
    form = DnsShopForm(request.POST or None)
    if form.is_valid():
        dns = form.save(commit=False)
        dns.shop = shop
        dns.save()
        request.flash['message'] = unicode(_("Dns successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('preferences_dns'))
    return render_to_response('preferences/preferences_dns.html', 
                              {'form': form,
                               'dnss': dnss
                               }, 
                              RequestContext(request))  


@shop_admin_required
def delete_dns(request, id):
    dns = get_object_or_404(DnsShop, pk=id)
    shop = request.shop
    if dns.shop != shop:
        raise Http404
    
    dns.delete()
    return HttpResponseRedirect(reverse('preferences_dns'))

@shop_admin_required
def edit_dns(request, id):
    dns = get_object_or_404(DnsShop, pk=id)
    shop = request.shop
    if dns.shop != shop:
        raise Http404
    
    if request.method != "POST":
        raise Http404
    
    domain_name = request.POST.get("dns")
    try:
        DnsShop.objects.get(dns=domain_name)
        request.flash["message"] = "A shop with that dns already exists."
        request.flash["severity"] = "error"
    except DnsShop.DoesNotExist:
        dns.dns = domain_name
        dns.save()
        request.flash["message"] = "DNS successfully updated."
        request.flash["severity"] = "success"
    
    return HttpResponseRedirect(reverse('preferences_dns'))

@shop_admin_required
def set_default_dns(request, id):
    dns = get_object_or_404(DnsShop, pk=id)
    shop = request.shop
    
    if dns.shop != shop:
        raise Http404
    
    try:
        older = DnsShop.objects.filter(shop=dns.shop, default=True).get()
        older.default = False
        older.save()
    except DnsShop.DoesNotExist:
        pass
    
    dns.default = True
    dns.save()
    
    return HttpResponseRedirect(reverse('preferences_dns'))


@shop_admin_required
def marketing(request):
    shop = request.shop
    preferences = shop.preference_set.all().get()
    form = MarketingForm(request.POST or None, instance=preferences)
    if form.is_valid():
        form.save()
        request.flash['message'] = unicode(_("Marketing data successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('web_store_marketing'))
    return render_to_response('store_admin/web_store/analytics.html', 
                              {'form': form}, 
                              RequestContext(request))

@shop_admin_required
def shows(request):
    from market_buy.models import Show
    from shops.models import DealerToShow
    shop = request.shop

    sort = request.GET.get('sort_by', 'date')
            
    assistant_to = DealerToShow.objects.filter(shop=shop)
    active_shows = Show.objects.filter(marketplace=shop.marketplace).filter(date_to__gte=datetime.datetime.now())
    
    if sort == "date": active_shows = active_shows.order_by("date_from")
    if sort == "-date": active_shows = active_shows.order_by("-date_from")
    if sort == "name": active_shows = active_shows.order_by("name")
    
    return render_to_response('store_admin/web_store/shows.html', 
                              {
                               'active_shows' : active_shows,
                               'assistant_to' : assistant_to,
                               }, 
                              RequestContext(request))


@shop_admin_required
def show_not_go(request, id):
    from shops.models import DealerToShow
    from market_buy.models import Show
    show = get_object_or_404(Show, pk=id)
    shop = request.shop
    
    assistant = DealerToShow.objects.filter(shop=shop, show=show).get()
    if assistant.shop != shop:
        raise Http404
    assistant.delete()
    
    return HttpResponseRedirect(reverse('web_store_shows'))


@shop_admin_required
def show_go(request, id):
    from shops.models import DealerToShow
    from market_buy.models import Show
    shop = request.shop
    show = get_object_or_404(Show, pk=id)
    
    assistant = DealerToShow.objects.get_or_create(shop=shop, show=show)  
    
    return HttpResponseRedirect(reverse('web_store_shows'))

@shop_admin_required
def add_show(request):
    from market_buy.models import Show
    from market_buy.forms import ShowForm
    shop = request.shop
    
    if request.method == "POST":
        form = ShowForm(request.POST)
        if form.is_valid():
            
            show = form.save(commit = False)
            show.marketplace = shop.marketplace
            show.save()
            
            request.flash['message'] = "Show added"
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('web_store_shows'))
    else:
        form = ShowForm()
    
    params = {'form' : form}
    return render_to_response("store_admin/web_store/show_add.html", params, RequestContext(request))
    

@shop_admin_required
def change_username_password(request):
    user = request.user
    form_username = UsernameChangeForm(request.POST or None, prefix="username", instance=user)
    form_password = PasswordChangeForm(user, request.POST or None, prefix="password")
    if form_password.is_valid() or form_username.is_valid():
        if form_password.is_valid():
            form_password.save()
            request.flash['message'] = unicode(_("Password successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('username_password'))
        if form_username.is_valid():
            form_username.save()
            request.flash['message'] = unicode(_("Username successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('username_password'))
    return render_to_response('store_admin/account/username_password.html', 
                              {'form_password': form_password,
                               'form_username': form_username}, 
                              RequestContext(request))


#@shop_admin_required
#def change_username(request):
#    user = request.user
#    form_username = UsernameChangeForm(request.POST or None, instance=user)
#    if form_username.is_valid():
#        form_username.save()
#        request.flash['message'] = unicode(_("Username successfully saved."))
#        request.flash['severity'] = "success"
#        return HttpResponseRedirect(reverse('username'))
#    return render_to_response('store_admin/account/username.html', 
#                              {'form_username': form_username}, 
#                              RequestContext(request))

@shop_admin_required
def change_profile(request):
    return render_to_response('store_admin/account/photo.html', {}, RequestContext(request))


@shop_admin_required
def change_password(request):
    user = request.user
    form_password = PasswordChangeForm(user, request.POST or None, prefix="password")
    if form_password.is_valid():
        form_password.save()
        request.flash['message'] = unicode(_("Password successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('account_password'))
    return render_to_response('store_admin/account/password.html', 
                              {'form_password': form_password}, 
                              RequestContext(request))
    
def send_template(request):
    from django.conf import settings
    from django.core.mail import send_mail
    
    try:
        shop = request.shop
        email = request.GET.get('email', None)
        id = long(request.GET.get('id', None))        
        
        notification = EmailNotification.objects.filter(id=id, shop=shop).get()
        
        send_mail(notification.subject,notification.body, settings.EMAIL_FROM, fail_silently=True)
        
        request.flash['message'] = unicode(_("Email sent."))
        request.flash['severity'] = "success"
        
    except Exception, e:
        request.flash['message'] = unicode(_("Can't send email."))
        request.flash['severity'] = "error"
        
    return HttpResponseRedirect(reverse("preferences_email"))