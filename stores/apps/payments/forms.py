import re
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from models import PayPalShopSettings, GoogleCheckoutShopSettings, ManualPaymentShopSettings, BraintreeShopSettings


class PayPalShopSettingsForm(ModelForm):
    
    class Meta:
        model = PayPalShopSettings
        exclude = ['shop']
    
    def clean_merchant_key(self):
        merchant_key = (self.cleaned_data.get("merchant_key", "")).strip()
        
        if merchant_key == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[\w]{22}", merchant_key): raise forms.ValidationError(_("Invalid Merchant Key number"))
        return merchant_key
        
class GoogleCheckoutShopSettingsForm(ModelForm):
    
    class Meta:
        model = GoogleCheckoutShopSettings
        exclude = ['shop']

    def clean_merchant_id(self):
        merchant_id = (self.cleaned_data.get("merchant_id", "")).strip()
        
        if merchant_id == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[0-9]{15}", merchant_id): raise forms.ValidationError(_("Invalid Merchant ID number"))
        return merchant_id 
    
    def clean_merchant_key(self):
        merchant_key = (self.cleaned_data.get("merchant_key", "")).strip()
        
        if merchant_key == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[\w]{22}", merchant_key): raise forms.ValidationError(_("Invalid Merchant Key number"))
        return merchant_key
        
class BraintreeShopSettingsForm(ModelForm):
    
    class Meta:
        model = BraintreeShopSettings
        exclude = ['shop']
        
    def clean_merchant_id(self):
        merchant_id = (self.cleaned_data.get("merchant_id", "")).strip()
        
        if merchant_id == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[\w]{16}", merchant_id): raise forms.ValidationError(_("Invalid Merchant Key number"))
        return merchant_id
    
    def clean_public_key(self):
        public_key = (self.cleaned_data.get("public_key", "")).strip()
        
        if public_key == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[\w]{16}", public_key): raise forms.ValidationError(_("Invalid Merchant Key number"))
        return public_key
    
    def clean_private_key(self):
        private_key = (self.cleaned_data.get("private_key", "")).strip()
        
        if private_key == "": raise forms.ValidationError(_("Required Field"))
        if not re.match("[\w]{16}", private_key): raise forms.ValidationError(_("Invalid Merchant Key number"))
        return private_key
    
class ManualPaymentShopSettingsForm(ModelForm):
    description = forms.CharField(label=_("Payment Description"), required=False)
    name = forms.CharField(label=_("Name"))
    
    class Meta:
        model = ManualPaymentShopSettings
        exclude = ['shop']
    
    def __init__(self, shop, *args, **kwargs):
        self.shop = shop
        super(ManualPaymentShopSettingsForm, self).__init__(*args, **kwargs)
        
    def clean_name(self):
        name = self.cleaned_data['name']
        name = name.strip()
        if len(name) == 0:
            raise forms.ValidationError(_("Name not valid"))
        
        if self.instance and self.instance.name == name:
            return name
        
        if ManualPaymentShopSettings.objects.filter(name__iexact=name).filter(shop=self.shop).count() > 0:
            raise forms.ValidationError(_("Name not available"))
        
        return name

        