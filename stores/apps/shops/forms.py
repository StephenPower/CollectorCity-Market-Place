import datetime

from django import forms
from auth.models import User
from django.utils.translation import ugettext as _
from django.forms import ModelForm
from django.contrib.localflavor.us.forms import USStateSelect, USZipCodeField

from sell.countries import COUNTRIES
from models import Shop, MailingListMember
from subscriptions.models import SubscriptionPlan


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


class ShopForm(forms.Form):
    name_store = forms.RegexField(max_length=60, label =_("Your shop's name"), regex=r'^[\s\w+-]+$',
            error_messages = {'invalid': _("This value may contain only letters, numbers and - character.")})
    
    shop_name = forms.CharField(max_length=60, label =_("Your shop's web address"))

    first_name = forms.CharField(label=_("First name"), max_length=50, required=True) 
    last_name = forms.CharField(label=_("Last name"), max_length=50, required=True)
        
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    
    email = forms.EmailField(label =_("E-mail"))
    
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    
    #Plan ID
    plan_id = forms.ModelChoiceField(queryset=SubscriptionPlan.objects.filter(active=True), empty_label=None)
    
    #Billing Address
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    state = forms.CharField(widget=USStateSelect)
    zip = USZipCodeField()
    
    #Billing information
    cc_number = forms.CharField(max_length=60, label =_("Credit Card Number"))
    cc_expiration_month = forms.ChoiceField(choices=MONTHS)
    cc_expiration_year = forms.ChoiceField(choices=YEARS)
    card_security_number = forms.CharField(max_length=4, label =_("Card Security Number"))
     
    terms = forms.BooleanField(required=False)    

    def clean_shop_name(self):
        shop_name = self.cleaned_data["shop_name"]
        try:
            Shop.objects.get(name=shop_name)
        except Shop.DoesNotExist:
            return shop_name
        raise forms.ValidationError(_("A shop with that name already exists."))


    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))


    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.filter(email = email).get()
        except User.DoesNotExist:
            user = None
        if user:
            raise forms.ValidationError(_("A user with that email already exists."))
        else:
            return email


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2


    def clean_terms(self):
        terms = self.cleaned_data["terms"]
        if terms:
            return terms
        else:
            raise forms.ValidationError(_("You must agree to the terms and conditions before you can create your account."))

class MailingListMemberForm(ModelForm):
    class Meta:
        model = MailingListMember
        exclude = ['shop']

