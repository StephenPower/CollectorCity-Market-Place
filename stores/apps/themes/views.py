import logging
import copy
import reversion
import os
import datetime
from django.core.files.base import ContentFile
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
 
from core.decorators import shop_required
from core.decorators import shop_admin_required
from reversion.models import Version

from forms import TemplateForm, AssetForm, AssetEditForm, ThemeImportForm
from models import Theme, Template, Asset


@shop_required
#@shop_admin_required
def theme(request, id=None):
    shop = request.shop
    theme = shop.theme
    edit = request.GET.get('edit', None)
    if id is None:
        template = Template.objects.filter(theme=theme, name='layout').get()
        edit = 'template'
    else:
        if edit == 'template':  
            template = get_object_or_404(Template, pk=id)
            if template.theme.shop != shop:
                raise Http404
        elif edit == 'asset':
            asset = get_object_or_404(Asset, pk=id)
            if asset.theme.shop != shop and asset.is_editable():
                raise Http404
            
    param = {}
    if edit == 'template':
        text = copy.copy(template.text)
        form_template = TemplateForm(request.POST or None, instance=template)
        if form_template.is_valid():
            if text != form_template.cleaned_data['text']:
                form_template.save()
#            request.flash['message'] = unicode(_("Template successfully saved."))
#            request.flash['severity'] = "success"
            return HttpResponse('Template successfully saved.')
            #return HttpResponseRedirect(reverse('web_store_theme', args=[template.id])+"?edit=template")
        version_list = Version.objects.get_for_object(template).order_by('-pk')[:10]
        param = {'form_template': form_template,
                 'version_list': version_list,
                 'template': template}

    else: # edit == 'asset'
    
        try: 
            if request.method == 'POST':
                form_asset = AssetEditForm(shop=shop, data=request.POST)
                if form_asset.is_valid():
                    text = form_asset.cleaned_data['text']
                    if asset.file.storage.exists(asset.file.name):
                        asset.file.storage.delete(asset.file.name)
                    asset.file.save(asset.file.name, ContentFile(str(text)))
                    
                    try:
                        asset.save()
                        asset.render()
                    except Exception,e:
                        return HttpResponse(e)
    
                    return HttpResponse('File successfully saved.')
                else:
                    errors = "\n".join(["%s" % (v.as_text()) for k,v in form_asset.errors.iteritems()])
                    return HttpResponse(errors)
            else:
                text = asset.file.read()
                form_asset = AssetEditForm(shop=shop, initial={'text':text})        
        
                param = {'form_asset': form_asset,
                         'asset': asset}
        except:
            logging.exception("MUERE!!!!!!!!!!!!!!!!!")
        
    param.update({'theme':theme,
                  'assets': shop.theme.asset_set.all(),
                  'templates': theme.get_templates(),
                 })
        
    return render_to_response('store_admin/web_store/theme.html', param, RequestContext(request))


@shop_required
@shop_admin_required
def theme_export(request):
    shop = request.shop
    theme = Theme.objects.filter(shop=shop).get()
    zip_file = open(theme.theme_export(), 'r')
    response = HttpResponse(FileWrapper(zip_file), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=theme.zip'
    return response


@shop_required

def theme_import(request):
    
    def handle_uploaded_file(f, filename):
        destination = open(filename, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    
    shop = request.shop
    theme = Theme.objects.filter(shop=shop).get()    
    if request.method == 'POST':
        form = ThemeImportForm(request.POST, request.FILES)
        if form.is_valid():
            
            file = request.FILES['file']
            filename = '%s%s_%s' % (settings.TMP_DIR, shop.name, file.name)
            handle_uploaded_file(file, filename)
        
            try:
                theme.theme_import(filename)
                request.flash['message'] = unicode(_("Theme successfully applied."))
                request.flash['severity'] = "success"
            except (Exception), e:
                request.flash['message'] = "Error when importing theme. %s" % e
                request.flash['severity'] = "error"
            finally:
                os.remove(filename)

            return HttpResponseRedirect(reverse('theme_import'))
    else:
        form = form = ThemeImportForm()
    return render_to_response('store_admin/web_store/theme_import.html',
                              {
                               'form': form,
                               'theme':theme,
                               'assets': shop.theme.asset_set.all(),
                               'templates': theme.get_templates(),                                 
                               },
                              RequestContext(request))


@shop_required
@shop_admin_required
@reversion.revision.create_on_success
def template_edit(request, id):
    shop = request.shop
    template = get_object_or_404(Template, pk=id)
    if template.theme.shop != shop:
        raise Http404
    text = copy.copy(template.text)
    form = TemplateForm(request.POST or None, instance=template)
    if form.is_valid():
        if text != form.cleaned_data['text']:
            form.save()
        request.flash['message'] = unicode(_("Template successfully edited."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('template_edit', args=[id]))
    version_list = Version.objects.get_for_object(template).order_by('-pk')[:10]
    return render_to_response('themes/template_edit.html',
                              {
                               'form': form,
                               'template': template,
                               'templates': shop.theme.template_set.all(),
                               'version_list': version_list,
                               },
                              RequestContext(request))

@shop_required
@shop_admin_required
def template_get_version(request, id):
    version = Version.objects.get(pk=id)
    template = version.get_object_version().object
    return HttpResponse(template.text)


@shop_required
@shop_admin_required
def asset_add(request):
    shop = request.shop
    theme = shop.theme
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.theme = shop.theme 
            asset.file.name = "%s_%s" % (shop.name, asset.file.name)
            asset.save()
            try:
                asset.render()
                request.flash['message'] = unicode(_("File successfully added."))
                request.flash['severity'] = "success"
            except Exception, e:
                request.flash['message'] = "Error in asset. %s" % e
                request.flash['severity'] = "error"
                asset.delete()
            return HttpResponseRedirect(reverse('asset_add'))
    else:
        form = AssetForm()
    return render_to_response('store_admin/web_store/theme_add_asset.html',
                              {
                               'form': form,
                               'theme':theme,
                               'assets': shop.theme.asset_set.all(),
                               'templates': theme.get_templates(),                               
                               },
                              RequestContext(request))


@shop_required
@shop_admin_required
def asset_delete(request, id):
    shop = request.shop
    asset = get_object_or_404(Asset, pk=id)
    if asset.theme.shop != shop:
        raise Http404
    asset.delete()
    request.flash['message'] = unicode(_("File successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('themes'))


@shop_required
@shop_admin_required
def asset_edit(request, id):
    shop = request.shop
    asset = get_object_or_404(Asset, pk=id)
    if asset.theme.shop != shop and asset.is_editable():
        raise Http404
    if request.method == 'POST':
        form = AssetEditForm(shop=shop, data=request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            asset.file.save(asset.file.name, ContentFile(str(text)))
            
            asset.save()
            asset.render()
            
            request.flash['message'] = unicode(_("File successfully edited."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('asset_edit', args=[id]))
    else:
        text = asset.file.read()
        form = AssetEditForm(shop=shop, initial={'text':text})
    return render_to_response('themes/asset_edit.html',
                              {
                               'form': form,
                               'asset': asset,
                               'templates': shop.theme.template_set.all(),
                               },
                              RequestContext(request))    
    
