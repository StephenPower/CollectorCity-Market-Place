from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

from models import AuctionSession
  
HOUR = [ (str(x).zfill(2), str(x).zfill(2)) for x in range(0,24)]
MINUTE = [ (str(x).zfill(2), str(x).zfill(2)) for x in range(0,60)]

class AuctionSessionForm(ModelForm):
    
    date_from = forms.DateField(label=_("Date from"))
    time_from = forms.TimeField(label=_("Time from"))
#    hour_from = forms.ChoiceField(choices=HOUR, label=_("Hour"))
#    minute_from = forms.ChoiceField(choices=MINUTE, label=_("Minute"))
    date_to = forms.DateField(label=_("Date to"))
    time_to = forms.TimeField(label=_("Time to"))
#    hour_to = forms.ChoiceField(choices=HOUR, label=_("Hour"))
#    minute_to = forms.ChoiceField(choices=MINUTE, label=_("Minute"))
    
    class Meta:
        model = AuctionSession
        fields= ['title', 'description']
        
    def clean_date_to(self):
        cleaned_data = self.cleaned_data
        dfrom = cleaned_data.get("date_from","")
        dto = cleaned_data.get("date_to","")
        if dfrom > dto:
            del cleaned_data["date_from"]
            self._errors["date_from"] =  ErrorList(["Date From must be earlier than Date To!"])
        return dto