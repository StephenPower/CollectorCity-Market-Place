import datetime
import logging

from django import forms
from django.conf import settings
from django.contrib.localflavor.us.forms import USStateSelect, USZipCodeField
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.translation import ugettext as _

from auth.models import User
from payments.gateways.braintreegw import BraintreeGateway
from subscriptions.models import SubscriptionPlan
from shops.models import Shop, ShopBillingInfo
from users.models import Profile 


MONTHS = (
    ("01", "January"),
    ("02", "February"),
    ("03", "March"),
    ("04", "April"),
    ("05", "May"),
    ("06", "June"),
    ("07", "July"),
    ("08", "August"),
    ("09", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December"),
)

current_year = datetime.date.today().year
YEARS = ((current_year + i, current_year + i) for i in range(31))

if getattr(settings, 'BRAINTREE_PRODUCTION', True):
    INITIAL_CC = None
else:
    INITIAL_CC = "4111111111111111"


class ShopInfoForm(forms.Form):
    name_store = forms.RegexField(max_length=60, label =_("Your shop's name"), regex=r'^[\s\w+-]+$',
            error_messages = {'invalid': _("This value may contain only letters, numbers and - character.")})
    shop_name = forms.CharField(max_length=60, label =_("Your shop's web address"), help_text=".greatcoins.com")
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    state = forms.CharField(widget=USStateSelect)
    zip = USZipCodeField()
    promotional_code = forms.CharField(max_length=100, required=False)
    
    def clean_shop_name(self):
        shop_name = self.cleaned_data["shop_name"]
        try:
            Shop.objects.get(name=shop_name)
        except Shop.DoesNotExist:
            return shop_name
        raise forms.ValidationError(_("A shop with that name already exists."))

    

class ShopBillingForm(forms.Form):
    
    #Billing Address
    billing_street = forms.CharField(max_length=100, required=True)
    billing_city = forms.CharField(max_length=100, required=True)
    billing_state = forms.CharField(widget=USStateSelect, required=True)
    billing_zip = USZipCodeField(required=True)
    
    #Billing information
    cc_number = forms.CharField(max_length=60, label =_("Credit Card Number"), initial=INITIAL_CC)
    cc_expiration_month = forms.ChoiceField(choices=MONTHS)
    cc_expiration_year = forms.ChoiceField(choices=YEARS)
    card_security_number = forms.CharField(max_length=4, label =_("Card Security Number"), required=True)

    terms = forms.BooleanField(required=False)
    
    def clean_terms(self):
        terms = self.cleaned_data["terms"]
        if terms:
            return terms
        else:
            raise forms.ValidationError(_("You must agree to the terms and conditions before you can create your account."))
    
    def clean(self):
        init_user = self.initial['user']
        cleaned_data = self.cleaned_data
        
#        try:
#            a = self.initial.get("result")
#            logging.critical(a)
#            return cleaned_data 
#        except Exception:
#            pass
#        
#        logging.critical("Trying to validate credit cards")
        
        if cleaned_data.has_key('cc_expiration_year') and cleaned_data.has_key('cc_expiration_month'):
            date_str =  "%s-%s" % (cleaned_data['cc_expiration_year'], cleaned_data['cc_expiration_month'])
            card_expire = datetime.datetime.strptime(date_str,  "%Y-%m")
        
            if card_expire < datetime.datetime.now():
                msg = u"Card expired."
                self._errors["cc_expiration_year"] = self.error_class([msg])
                self._errors["cc_expiration_month"] = self.error_class([msg])
    
                # These fields are no longer valid. Remove them from the
                # cleaned data.
                del cleaned_data["cc_expiration_year"]
                del cleaned_data["cc_expiration_month"]
        
        bt_gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        
        first_name = init_user.first_name
        last_name = init_user.first_name
        email = init_user.email
        cc_number = cleaned_data.get("cc_number", None)
        if cc_number is None: self._errors["cc_number"] = self.error_class(["This field is required!"])
        
        month = cleaned_data.get("cc_expiration_month", None)
        year = cleaned_data.get("cc_expiration_year", None)
        
        if month is None or year is None:
            raise forms.ValidationError(_("Expiration date invalid format."))
                
        cc_expiration_date = "%s/%s" % (month, year)
        cc_security_number = cleaned_data.get("card_security_number", None)
        if cc_security_number is None: self._errors["card_security_number"] = self.error_class(["This field is required!"])
        
        street = cleaned_data.get("billing_street", None)
        if street is None: self._errors["billing_street"] = self.error_class(["This field is required!"])
        city = cleaned_data.get("billing_city", None)
        if city is None: self._errors["billing_city"] = self.error_class(["This field is required!"])
        state = cleaned_data.get("billing_state", None)
        if state is None: self._errors["billing_state"] = self.error_class(["This field is required!"])
        zip = cleaned_data.get("billing_zip", None)
        if zip is None: forms.ValidationError(_(""))
                
        shop_name = "thisisafake.shop.com"
        shop_id = "-1"
        
        result = bt_gw.create_customer(first_name, last_name, email, cc_number, cc_expiration_date, cc_security_number, street, city, state, zip, shop_name, shop_id)
        if result.is_success:
            self.result = result
            self.initial["result"] = result
        else:
            raise forms.ValidationError(_(result.message))
        
        return  cleaned_data

class ShopPlanForm(forms.Form):
    #Plan ID
    plan_id = forms.ModelChoiceField(queryset=SubscriptionPlan.objects.filter(active=True), empty_label=None)
        


from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

class ShopSignUpWizard(FormWizard):

    def process_step(self, request, form, step):
        if step == 0:
            from subscriptions.models import SubscriptionPlan
            
            promotional_code = request.POST.get("0-promotional_code", None)
            
            if promotional_code != u'' and promotional_code is not None:
                plans = SubscriptionPlan.objects.filter(active=True).filter(secret_code=promotional_code)
            else:
                plans = SubscriptionPlan.objects.filter(active=True).filter(visible=True).order_by('-price')
            self.extra_context = {'plans': plans, 'promotional_code': promotional_code}
    
    
    def parse_params(self, request, *args, **kwargs):
        current_step = self.determine_step(request, *args, **kwargs)
        if request.method == 'POST' and current_step == 2:
            self.initial[2] = {'user' : request.user }

    def get_template(self, step):
        return 'default/sell/signup_wizard_%s.html' % step
    
    @transaction.commit_on_success
    def done(self, request, form_list):
        user = request.user
        
        cleaned_data = {}
        [cleaned_data.update(form.cleaned_data) for form in form_list]
        
        plan_id = cleaned_data['plan_id'].plan_id
        
        #Update address
        profile = user.get_profile()
        profile.street_address = cleaned_data['street']
        profile.city = cleaned_data['city']
        profile.state = cleaned_data['state']
        profile.zip = cleaned_data['zip']
        profile.country = 'United States'
        profile.save()
        
        billing_street = cleaned_data['billing_street'].encode('ascii', 'ignore')
        billing_city = cleaned_data['billing_city'].encode('ascii', 'ignore')
        billing_state = cleaned_data['billing_state'].encode('ascii', 'ignore')
        billing_zip = cleaned_data['billing_zip'].encode('ascii', 'ignore')
        
        date_str =  "%s-%s" % (cleaned_data['cc_expiration_year'], cleaned_data['cc_expiration_month'])
        card_expire = datetime.datetime.strptime(date_str,  "%Y-%m")
        
        
        """ Create shop """
        shop = Shop.objects.create(marketplace=request.marketplace,
                                   name=cleaned_data['shop_name'].lower(), 
                                   admin=user,
                                   name_store=cleaned_data['name_store'])
        
        """ Braintree subscription """
        #Create a new Customer with Financial data in braintree
        bt_gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
        
        result = (form_list[2]).result

        if result.is_success:
            customer_id = result.customer.id
            update = bt_gw.update_customer_shopname(customer_id, shop.id, shop.default_dns)
            
            if update.is_success:
                token = result.customer.credit_cards[0].token    
            else:
                transaction.rollback()
                request.flash['message'] = unicode(_("%s" % update.message))
                request.flash['severity'] = "error"
                return HttpResponseRedirect(reverse('market_sell_signup'))    
            
        else:
            transaction.rollback()
            logging.error(result.errors.errors.data)
            logging.error(result.message)
            request.flash['message'] = unicode(_("%s" % result.message))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('market_sell_signup'))
        
        #Create a Subscription in braintree linked to the customer created before
        result = bt_gw.create_subscription(plan_id, token)
        if result.is_success:
            profile = user.get_profile()
            profile.set_subscription_plan(plan_id, result.subscription.id)    
        else:
            transaction.rollback()
            request.flash['message'] = unicode(_("Could not create the subscription. %s.Please contact us.") % result.message)
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('market_sell_signup'))
        
        #Store billing information
        billing = ShopBillingInfo(
            shop = shop,
            card_ending = cleaned_data['cc_number'][-4:],
            card_expire = card_expire, 
            street = billing_street,
            city = billing_city,
            state = billing_state,
            zip = billing_zip,
        )
        billing.save()
        
        request.flash['message'] = unicode(_("Shop successfully added."))
        request.flash['severity'] = "success"
            
        return HttpResponseRedirect(reverse('market_sell_welcome', args=[shop.id]))
