#from django.forms import ModelForm
#
#from models import Category, SubCategory
#  
#
#class CategoryForm(ModelForm):
#    class Meta:
#        model = Category 
#        exclude = ['shop']
#
#
#class SubCategoryForm(ModelForm):
#    class Meta:
#        model = SubCategory
#        fields = ['category', 'name']
#        
#    def __init__(self, request=None, *args, **kwargs):
#        super(SubCategoryForm, self).__init__(*args, **kwargs)
#        # Filter categorys for specific shop 
#        if request:
#            self.shop = request.shop
#            category = self.fields.get('category')
#            category.queryset = Category.objects.filter(shop=self.shop)
