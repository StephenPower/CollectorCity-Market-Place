from django.forms import ModelForm

from market.models import MarketCategory, MarketSubCategory, MarketMailingListMember, MarketPostComment
  

class MarketPostCommentForm(ModelForm):
    class Meta:
        model = MarketPostComment 
        exclude = ['user', 'post']


class MarketCategoryForm(ModelForm):
    class Meta:
        model = MarketCategory 
        exclude = ['marketplace']


class MarketSubCategoryForm(ModelForm):
    class Meta:
        model = MarketSubCategory
        fields = ['marketplace', 'slug', 'category']
        
#    def __init__(self, request=None, *args, **kwargs):
#        super(MarketSubCategoryForm, self).__init__(*args, **kwargs)
#        # Filter categorys for specific shop 
#        if request:
#            self.marketplace = request.marketplace
#            category = self.fields.get('category')
#            category.queryset = Category.objects.filter(shop=self.shop)

class MarketMailingListMemberForm(ModelForm):
    class Meta:
        model = MarketMailingListMember
        exclude = ['marketplace']
