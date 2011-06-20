import re, logging
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.contrib.localflavor.us.forms import USStateSelect,\
    USPhoneNumberField

from models import Preference, ShippingWeight, ShippingPrice, ShippingItem, TaxState, DnsShop, EmailNotification
from preferences.models import ShopPolicies
from auth.models import User
from users.models import Profile


class GeneralPreferenceForm(ModelForm):
    email = forms.EmailField(required=False)
    phone = USPhoneNumberField(required=False)
    
    class Meta:
        model = Preference
        fields = ['name_store', 'email', 'phone']

class ProfileForm(ModelForm):
    state = forms.CharField(widget=USStateSelect)
    
    class Meta:
        model = Profile
        fields = ['street_address', 'zip', 'city', 'state', 'country', ]
    
    def clean_zip(self):
        zip = self.cleaned_data.get("zip", "")
        if zip.strip() == "": raise forms.ValidationError("Zip is a required field.")
        
        if not (re.match("[0-9]{5}(-[0-9]{4})?$", zip)): raise forms.ValidationError("Invalid Zip code. Valid formats are XXXXX or XXXXX-XXXX")   
        return zip
    
    def clean_country(self):
        country = self.cleaned_data.get("country", "")
        if country.strip() == "": raise forms.ValidationError("Country is a required field.")
        return country
    
    def clean_street_address(self):
        street = self.cleaned_data.get("street_address", "")
        if street.strip() == "": raise forms.ValidationError("Street is a required field.")
        return street
    
    def clean_city(self):
        city = self.cleaned_data.get("city", "")
        if city.strip() == "": raise forms.ValidationError("City is a required field.")
        return city

class TaxesPreferenceForm(ModelForm):
    class Meta:
        model = Preference
        fields = ['taxes_same_state_store', 'taxes_to_shipping_fees']


class TaxStateForm(ModelForm):
    #state = forms.CharField(widget=USStateSelect)
    tax = forms.DecimalField(help_text=_("Enter a state tax rate number (between 1 and 100)"))
    
    class Meta:
        model = TaxState
        exclude = ['shop']
        
    
    def __init__(self, shop, *args, ** kwargs):
        
        self.shop = shop
        super(TaxStateForm, self).__init__(*args, ** kwargs)
        
    def clean_state(self):
        state = self.cleaned_data['state']
        try:
            TaxState.objects.get(shop=self.shop, state=state)
        except TaxState.DoesNotExist:
            return state
        raise forms.ValidationError(_("A tax for state %s already exists." % state))

    def clean_tax(self):
        
        tax = self.cleaned_data['tax']
        if tax < 0:
            raise forms.ValidationError(_("A tax has to be more or equal 0%"))
        elif tax > 100:
            raise forms.ValidationError(_("A tax has to be less than 100%"))
        return tax
            
class TaxStateEditForm(ModelForm):
    
    class Meta:
        model = TaxState
        exclude = ['shop', 'state']
        
    def __init__(self, shop, *args, ** kwargs):
        
        self.shop = shop
        super(TaxStateEditForm, self).__init__(*args, ** kwargs)    
    
    def clean_tax(self):
        
        tax = self.cleaned_data['tax']
        if tax < 0:
            raise forms.ValidationError(_("A tax has to be more or equal 0%"))
        elif tax > 100:
            raise forms.ValidationError(_("A tax has to be less than 100%"))
        return tax

class AuctionsPreferenceForm(ModelForm):
    class Meta:
        model = Preference
        fields = ['allow_sessions', 'allow_open_auctions', 'default_days', 'open_auto_extend', 'session_auto_extend']
    

class DnsShopForm(ModelForm):
    class Meta:
        model = DnsShop
        exclude = ['shop']
        
    def clean_dns(self):
        dns = self.cleaned_data['dns']
        try:
            DnsShop.objects.get(dns=dns)
        except DnsShop.DoesNotExist:
            return dns
        raise forms.ValidationError(_("A shop with that dns already exists."))        
        
        
class ShippingWeightForm(ModelForm):
    class Meta:
        model = ShippingWeight
        exclude = ['shop']


class ShippingPriceForm(ModelForm):
    class Meta:
        model = ShippingPrice
        exclude = ['shop']


class ShippingItemForm(ModelForm):
    class Meta:
        model = ShippingItem
        exclude = ['shop']
        

class EmailNotificationForm(ModelForm):
    class Meta:
        model = EmailNotification
        fields = ['subject', 'body']

        
class ShopPoliciesForm(ModelForm):
    class Meta:
        model = ShopPolicies
        fields = ['refund_policy', 'privacy_policy', 'terms_of_service']


class MarketingForm(ModelForm):
    class Meta:
        model = Preference
        fields = ['google_analytics_account_number']
        
    def clean_google_analytics_account_number(self):
        google_analytics_account_number = self.cleaned_data['google_analytics_account_number']
        if re.match(r"^\w{2}\-\d{4,8}\-\d$", google_analytics_account_number) is None:
            raise forms.ValidationError('Invalid analitycs account number')
        return google_analytics_account_number
        
        

class UsernameChangeForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    
    class Meta:
        model = User
        fields = ['username']