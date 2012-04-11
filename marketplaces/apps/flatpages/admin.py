from django import forms
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/]+$',
        help_text = _("Example: '/about/contact/'. Make sure to have leading"
                      " and trailing slashes."),
        error_message = _("This value must contain only letters, numbers,"
                          " underscores, dashes or slashes."))

    class Meta:
        model = FlatPage


class FlatPageAdmin(admin.ModelAdmin):
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'marketplace')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('marketplace', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')

#    class Media:
#        js = ('js/tiny_mce/tiny_mce.js', 'js/textareas.js')

admin.site.register(FlatPage, FlatPageAdmin)
