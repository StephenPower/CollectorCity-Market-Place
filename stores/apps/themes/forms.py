import re

from django.forms import ModelForm
from django import forms

from models import Template, Asset, UPLOAD_DIR
from render import render_asset

IMPORT_DIR = 'import'

class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields= ['text']

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields= ['file']
    
    def save(self, commit=True):
        asset = super(AssetForm, self).save(commit=False)
        name = self.instance.file.name
        asset.name = re.sub(UPLOAD_DIR+'/','',name)
        if commit:
            asset.save()
        return asset
        
        
class AssetEditForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, shop=None, request=None, *args, **kwargs):
        self.shop = shop
        super(AssetEditForm, self).__init__(*args, **kwargs)
        
    
    def clean_text(self):
        text = self.cleaned_data['text']
        try:
            render_asset(text, self.shop)
        except (Exception), e:
            raise forms.ValidationError(e)
        return text


class ThemeImportForm(forms.Form):
    file = forms.FileField()

