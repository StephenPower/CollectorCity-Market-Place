import copy

from django import forms
from django.forms import ModelForm

from models import Post, Home, About, Page, Link, DynamicPageContent

PAGES_DEFAULT = [
                 ('/home/','Home'),
                 ('/auctions/','Auctions'), 
                 ('/for_sale/','For sale'), 
                 ('/blog/','Blog'), 
                 ('/about_us/','About Us'), 
                ]

PAGES = 'pages'
  
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields= ['title', 'body', 'meta_content']
      
        
class HomeForm(ModelForm):
    class Meta:
        model = Home
        fields = ['title', 'body', 'meta_content', 'image'] 
        
        
class AboutForm(ModelForm):
    class Meta:
        model = About
        fields = ['title', 'body', 'meta_content'] 
        
class PageForm(ModelForm):
    
    class Meta:
        model = Page
        fields = ['name', 'name_link', 'title', 'body', 'meta_content', 'visible']
    
    def __init__(self, shop, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.shop = shop
        
    def clean_name(self):
        old = self.instance.name
        name = self.cleaned_data["name"]
        try:
            page = Page.objects.filter(name=name, shop=self.shop).get()
            if page.name != old:
                raise forms.ValidationError("A page with that name already exists in your shop.")
            return name
        except Page.DoesNotExist:
            return name
        

    def clean_name_link(self):
        old = self.instance.name_link
        name_link = self.cleaned_data["name_link"]
        try:
            page = Page.objects.filter(name_link=name_link, shop=self.shop).get()
            if page.name_link != old:
                raise forms.ValidationError("A page with that name link already exists in your shop.")
            return name_link
        except Page.DoesNotExist:
            return name_link
        

    
class DynamicPageForm(ModelForm):
    
    class Meta:
        model = DynamicPageContent
        fields = ['meta_content']
    
    def __init__(self, shop, *args, **kwargs):
        super(DynamicPageForm, self).__init__(*args, **kwargs)
        self.shop = shop
        

class LinkForm(ModelForm):
    to = forms.ChoiceField()  
    
    class Meta:
        model = Link
        fields = ['name', 'to', 'title']
    
    def __init__(self, shop, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        
        l = copy.copy(PAGES_DEFAULT)
        pages = Page.objects.filter(shop=shop)
        for page in pages:
            l.append(( "/%s/%s/" % (PAGES, page.name_link), page.name))
        to = self.fields.get('to')
        to.choices = l
        