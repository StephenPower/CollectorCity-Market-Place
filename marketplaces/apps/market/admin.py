from django.contrib import admin

from market.models import MarketPlace, MarketPlaceSettings, MarketCategory, MarketSubCategory, MarketMailingListMember,\
    MarketBlogPost, MarketPostCategory, MarketPostComment, MarketPostPick,\
    PrivacyPolicy, TermsAndConditions


class MarketPlaceSettingsInline(admin.StackedInline):
    model = MarketPlaceSettings

class MarketPlaceAdmin(admin.ModelAdmin):
    inlines = [MarketPlaceSettingsInline]


admin.site.register(MarketPlace, MarketPlaceAdmin)
admin.site.register(MarketPostCategory)
admin.site.register(MarketPostComment)
admin.site.register(MarketPostPick)
admin.site.register(MarketCategory)
admin.site.register(MarketSubCategory)
admin.site.register(MarketMailingListMember)


#class PrivacyPolicyAdmin(admin.ModelAdmin):
#    class Media:
#        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')
# 
#class TermsAndConditionsAdmin(admin.ModelAdmin):
#    class Media:
#        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')
#
#class MarketBlogPostAdmin(admin.ModelAdmin):
#    class Media:
#        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')
#
#
#admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
#admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
#admin.site.register(MarketBlogPost, MarketBlogPostAdmin)

admin.site.register(PrivacyPolicy)
admin.site.register(TermsAndConditions)
admin.site.register(MarketBlogPost)
