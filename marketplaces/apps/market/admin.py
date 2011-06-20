from django.contrib import admin

from market.models import MarketPlace, MarketCategory, MarketSubCategory, MarketMailingListMember,\
    MarketBlogPost, MarketPostCategory, MarketPostComment, MarketPostPick,\
    PrivacyPolicy, TermsAndConditions

admin.site.register(MarketBlogPost)
admin.site.register(MarketPostCategory)
admin.site.register(MarketPostComment)
admin.site.register(MarketPostPick)
admin.site.register(MarketCategory)
admin.site.register(MarketSubCategory)
admin.site.register(MarketPlace)
admin.site.register(MarketMailingListMember)


class PrivacyPolicyAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')
 
class TermsAndConditionsAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')
 
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)