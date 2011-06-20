from models import *
from django.contrib import admin
from reversion.admin import VersionAdmin

admin.site.register(Theme)
#admin.site.register(Template)
admin.site.register(Asset)
admin.site.register(AssetRendering)


class TemplateAdmin(VersionAdmin):
    pass

admin.site.register(Template, TemplateAdmin)