from django import forms
from captcha.fields import CaptchaField
from market.models import MarketCategory, MarketSubCategory, MarketMailingListMember, MarketPostComment


class MarketPostCommentForm(forms.ModelForm):
    class Meta:
        model = MarketPostComment 
        exclude = ['user', 'post']


class MarketCategoryForm(forms.ModelForm):
    class Meta:
        model = MarketCategory 
        exclude = ['marketplace']


class MarketSubCategoryForm(forms.ModelForm):
    class Meta:
        model = MarketSubCategory
        fields = ['marketplace', 'slug']
        
#    def __init__(self, request=None, *args, **kwargs):
#        super(MarketSubCategoryForm, self).__init__(*args, **kwargs)
#        # Filter categorys for specific shop 
#        if request:
#            self.marketplace = request.marketplace
#            category = self.fields.get('category')
#            category.queryset = Category.objects.filter(shop=self.shop)

class MarketMailingListMemberForm(forms.ModelForm):
    class Meta:
        model = MarketMailingListMember
        exclude = ['marketplace']

class ContactForm(forms.Form):
    name = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()
