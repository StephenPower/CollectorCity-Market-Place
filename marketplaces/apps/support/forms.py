from django import forms

from support.models import FeaturesHelpText

class FeaturesHelpTextForm(forms.ModelForm):
    
    class Meta:
        model = FeaturesHelpText   