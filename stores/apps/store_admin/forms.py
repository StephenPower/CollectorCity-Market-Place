import datetime
import logging

from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField

class EmailContactForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    question = forms.CharField(widget=forms.Textarea, required=False)
    
class PhoneContactForm(forms.Form):
    name = forms.CharField(required=False)
    phone = USPhoneNumberField(required=False)
    messenger_id = forms.CharField(required=False)
    
class CreditCardForm(forms.Form):
    card_holder_name = forms.CharField(max_length=60)
    card_number = forms.CharField(max_length=20)
    expiration_date = forms.CharField(max_length=7)
    security_number = forms.CharField(max_length=4)