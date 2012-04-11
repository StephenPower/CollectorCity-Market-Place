import re
from django import forms 

from sell.models import ShippingData
from django.contrib.localflavor.us.forms import USStateSelect, USZipCodeField

class ShippingDataForm(forms.ModelForm):
    state = forms.CharField(widget=USStateSelect)
    save_shipping_info = forms.BooleanField(label="Save Shipping Information", widget=forms.CheckboxInput(), required=False)
    
    class Meta:
        model = ShippingData
        
    def clean_zip(self):
        zip = self.cleaned_data.get("zip", "")
        if zip.strip() == "": raise forms.ValidationError("Zip is a required field.")
        
        if not (re.match("[0-9]{5}(-[0-9]{4})?$", zip)): raise forms.ValidationError("Invalid Zip code. Valid formats are XXXXX or XXXXX-XXXX")   
        return zip
    
    def clean(self):
        first_name = self.cleaned_data.get("first_name", "")
        last_name = self.cleaned_data.get("last_name", "")
        country = self.cleaned_data.get("country", "")
        street = self.cleaned_data.get("street_address", "")
        city = self.cleaned_data.get("city", "")
        
        if first_name.strip() == "": raise forms.ValidationError("First name is a required field.")
        if last_name.strip() == "": raise forms.ValidationError("First name is a required field.")
        if street.strip() == "": raise forms.ValidationError("Street is a required field.")
        if city.strip() == "": raise forms.ValidationError("City is a required field.")
        if country.strip() == "": raise forms.ValidationError("Country is a required field.")
        
        return self.cleaned_data
    
    def save_shipping(self):
        return self.cleaned_data.get("save_shipping_info", False)
