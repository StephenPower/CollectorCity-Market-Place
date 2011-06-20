"""
    Shop Theme handling application models
"""
import logging
import mimetypes
import zipfile
import re
import reversion
import os

from django.db import models
from django.db.models.fields.related import OneToOneField
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from reversion import revision

from shops.models import Shop 


TEMPLATES = [
             'layout',
             'home',
             'blog',
             'about_us',
             'search',
             'page',
             'for_sale',
             'view_item',
             'auctions',
             'view_lot',
             'view_history_lot',
             'view_post',
             'login',
             'register',
             'welcome',
             'my_shopping',
             'my_orders',
             'confirm',
             'manual_payment',
             'shipping',
             '404',
             'payment_success',
             'payment_cancel',
             'payment_paypal_confirm',
             ]

PAGES = [
         #'about_us',
         'auctions',
         'blog',         
         'for_sale',         
         'page',
         'search',
         'view_item',         
         'view_history_lot',
         'view_lot',         
         'view_post',
         ]

OTHER_PAGES = [
               'login',
               'register',
               'welcome',
               'my_shopping',
               'my_orders',
               'confirm',
               'manual_payment',
               'shipping',
               '404',
               'payment_success',
               'payment_cancel',
               'payment_paypal_confirm',
              ]


UPLOAD_DIR = 'asset'

EDITABLE_TYPES = ['text/css', 'application/x-javascript']


class Theme(models.Model):
    shop = models.OneToOneField(Shop)
    
    def __unicode__(self):
        return self.shop.name

    def home_id(self):
        return Template.objects.filter(name='home', theme=self).get().id

    def about_us_id(self):
        return Template.objects.filter(name='about_us', theme=self).get().id
    
    def layout_id(self):
        return Template.objects.filter(name='layout', theme=self).get().id

    def get_templates(self):
        dic = {'pages':[], 'other_pages':[]}
        for template in self.template_set.all():
            if template.name in PAGES:
                dic['pages'].append(template)
            if template.name in OTHER_PAGES:
                dic['other_pages'].append(template)
        return dic
    
    @classmethod
    def create_default(cls, shop):
        try:
            theme = Theme.objects.filter(shop = shop).get()
        except Theme.DoesNotExist:
            theme = Theme(shop=shop)
            theme.save()
        #Template.create_default(theme)
        theme.theme_import('%s%s' % (settings.THEMES_ROOT, settings.DEFAULT_THEME))

    def get_template(self, name):
        template = Template.objects.filter(theme=self, name=name)[0]
        return template.text
        
    def theme_export(self):
        # create zip
        if not os.path.isdir(settings.TMP_DIR):
            os.mkdir(dir)
        zip_name = "%s%s_%s" % (settings.TMP_DIR, self.shop.name, 'export.zip')
        zip = zipfile.ZipFile(zip_name, 'w')

        # for in templates and insert templates in zip
        for template in self.template_set.all():
            filename = '%s%s_%s.html' % (settings.TMP_DIR, self.shop.name, template.name)
            temp = open(filename, 'a+b')
            try:
                temp.write(template.text)
            finally:
                temp.close()
                zip.write(str(filename), str('templates/%s.html' % template.name), zipfile.ZIP_DEFLATED)
                os.remove(filename)
            
        # for in assets and insert in zip file
        for asset in self.asset_set.all():
            data = asset.file.read()
            info = zipfile.ZipInfo()
            info.filename = str('assets/%s' % asset.name)
            info.external_attr = 0777 << 16L
            info.compress_type = zipfile.ZIP_DEFLATED             
            zip.writestr(info, data)
        
        zip.close()
        return zip.filename
    
    @revision.create_on_success
    def theme_import(self, filename):
        # load zip file
        zip = zipfile.ZipFile(filename, 'r')

        # check the structure file
        asset_ok = False
        template_ok = False
        for i in zip.namelist():
            if asset_ok and template_ok:
                break
            match = re.search(r"^assets/(?P<name>.*)", i)
            if match:
                asset_ok = True
            match = re.search(r"^templates/(?P<name>.*)", i)
            if match:
                template_ok = True
        if not (asset_ok and template_ok):
            raise Exception("The theme does not have the expected structure.")
            
        # load templates of theme from files
        for template_name in TEMPLATES:
            try:
                template = Template.objects.get(theme=self, name=template_name)
            except Template.DoesNotExist: 
                template = Template(theme=self, name=template_name)
            text = zip.read(str('templates/%s.html' % template_name))
            if template.text != text:
                template.text = text 
                template.save()
        
        # delete actual_assets
        for asset in Asset.objects.filter(theme=self):
            asset.delete()    
        
        # load new assets
        filelist = zip.filelist   
        for info in filelist:
            match = re.search(r"^assets/(?P<name>.+)", info.filename)
            if match:
                name = match.group('name')
                asset = Asset()
                asset.theme = self
                asset.name = name
                asset.file.save("%s_%s"%(self.shop.name, name), ContentFile(zip.read(info.filename)))
                asset.save()
        
        # render editables assets
        for asset in Asset.objects.filter(theme=self):
            if asset.is_editable():
                asset.render()
            
        
        
class Template(models.Model):
    theme = models.ForeignKey(Theme)
    name = models.CharField(max_length=60)
    last_updated =  models.DateTimeField(auto_now=True)
    text = models.TextField()
    
    def __unicode__(self):
        return u"%s for %s" % (self.name, self.theme)
    
#    @classmethod
#    def create_default(self, theme):
#        for template_name in TEMPLATES:
#            try:
#                Template.objects.get(theme=theme, name=template_name)
#            except Template.DoesNotExist: 
#                template = Template(theme=theme, name=template_name)
#                name_file = '%s/bidding/default/%s.html' % (settings.STORE_TEMPLATES, template_name)
#                try:
#                    file = open(name_file, 'r')
#                    template.text = file.read()
#                    template.save()
#                except IOError:
#                    logging.exception("Error making default template")
#                    raise
#                else:
#                    file.close()

reversion.register(Template)


asset_storage = default_storage
try:
    from storages.backends.s3boto import S3BotoStorage
    asset_storage = S3BotoStorage(bucket=settings.AWS_STORAGE_BUCKET_NAME, 
                            access_key=settings.AWS_ACCESS_KEY_ID, 
                            secret_key=settings.AWS_SECRET_ACCESS_KEY, 
                            acl='public-read', headers=settings.AWS_HEADERS, 
                            querystring_auth=False, custom_domain=False, secure_urls=False)
except (AttributeError, ImportError):
    pass

class Asset(models.Model):
    theme = models.ForeignKey(Theme)
    file = models.FileField(upload_to=UPLOAD_DIR, storage=asset_storage)
    last_updated =  models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.file.name
    
    def file_type(self):
        return mimetypes.guess_type(self.file.name)[0]

    def is_editable(self):
        return self.file_type() in EDITABLE_TYPES

    def render(self):
        from render import render_asset
        if self.is_editable(): 
    
            text = self.file.read()
            
            render = render_asset(text, self.theme.shop)
            try:
                file = self.assetrendering.file
                if file.storage.exists(file.name):
                    file.storage.delete(file.name)
                file.save(file.name, ContentFile(str(render)))
            except AssetRendering.DoesNotExist:
                asset_rendering = AssetRendering(asset=self)
                asset_rendering.file.save("%s_render_%s" % (self.theme.shop.name, self.name),ContentFile(str(render)))
                asset_rendering.save()


            render_secure = render_asset(text, self.theme.shop, is_secure=True)
            try:
                file = self.assetrenderingsecure.file
                if file.storage.exists(file.name):
                    file.storage.delete(file.name)
                file.save(file.name, ContentFile(str(render_secure)))
            except AssetRenderingSecure.DoesNotExist:
                asset_rendering_secure = AssetRenderingSecure(asset=self)
                asset_rendering_secure.file.save("%s_render_secure_%s" % (self.theme.shop.name, self.name),ContentFile(str(render_secure)))
                asset_rendering_secure.save()


    
class AssetRendering(models.Model):
    asset = OneToOneField(Asset)
    file = models.FileField(upload_to=UPLOAD_DIR, storage=asset_storage)


class AssetRenderingSecure(models.Model):
    asset = OneToOneField(Asset)
    file = models.FileField(upload_to=UPLOAD_DIR, storage=asset_storage)
