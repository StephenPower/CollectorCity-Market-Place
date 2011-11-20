import logging

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse,\
    HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

#from django.core.paginator import Paginator, InvalidPage, EmptyPage

from forms import PostForm, HomeForm, AboutForm, PageForm, LinkForm, DynamicPageForm
from models import Post, Page, Home, About, Menu, Link, DynamicPageContent

from core.decorators import shop_admin_required, add_page_feature_enabled
from blog_pages.models import PageVersion

@shop_admin_required    
def post_add(request):
    shop = request.shop
    form = PostForm(request.POST or None)
    posts = Post.objects.filter(shop=shop).filter(draft=False).order_by('-date_time')
    drafts = Post.objects.filter(shop=shop).filter(draft=True)
    if form.is_valid():
        post = form.save(commit = False)
        post.shop = shop
        post.save() 
        request.flash['message'] = unicode(_("Post successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('web_store_blogs'))
    return render_to_response('store_admin/web_store/blog_post_add.html', 
                              {'form': form,
                               'drafts': drafts,
                               'posts': posts},
                              RequestContext(request))


@login_required
@shop_admin_required    
def post_edit(request, id):
    post = get_object_or_404(Post, pk=id)
    shop = request.shop
    posts = Post.objects.filter(shop=shop).filter(draft=False).order_by('-date_time')
    drafts = Post.objects.filter(shop=shop).filter(draft=True)
    if post.shop != shop:
        raise Http404
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save(commit = False)
        post.shop = shop
        post.save() 
        request.flash['message'] = unicode(_("Post successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('post_edit', args=[id]))
    return render_to_response('store_admin/web_store/blog_post_edit.html', 
                              {'form': form,
                               'post': post,
                               'drafts': drafts,
                               'posts': posts},
                              RequestContext(request))


@shop_admin_required
def post_delete(request, id):
    post = get_object_or_404(Post, pk=id)
    shop = request.shop
    if post.shop != shop:
        raise Http404
    post.delete()
    request.flash['message'] = unicode(_("Post successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('web_store_blogs'))

@shop_admin_required
def post_publish(request, id):
    post = get_object_or_404(Post, pk=id)
    shop = request.shop
    if post.shop != shop:
        raise Http404
    value = bool(int(request.GET.get("p", 1)))
    post.publish(value)
    request.flash['message'] = unicode(_("Post published."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('web_store_blogs'))

@shop_admin_required
def post_publish_all(request):
    shop = request.shop
    if request.method != "POST":
        raise Http404
    
    keys = request.POST.getlist("keys")
    for id in keys:
        post = get_object_or_404(Post, pk=int(id))
        post.publish(True)
                
    request.flash['message'] = unicode(_("Posts published."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('web_store_blogs'))


@shop_admin_required
def page_edit_home(request):
    shop = request.shop
    static_pages = Page.objects.filter(shop=shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop=shop)
    try:
        home = Home.objects.filter(shop=shop).get()
    except:
        home = Home(shop=shop)
        home.save()

    if request.POST:
        form = HomeForm(request.POST, request.FILES, instance=home)
        if form.is_valid():
            form.save()
            request.flash['message'] = unicode(_("Page successfully saved."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('page_edit_home'))
    else:
        form = HomeForm(instance=home)
    return render_to_response('store_admin/web_store/pages_edit_home.html',
                              {'form': form, 'home': home, 'static_pages': static_pages, 'dynamic_pages': dynamic_pages},
                              RequestContext(request))


@shop_admin_required
def page_edit_about(request):
    shop = request.shop
    static_pages = Page.objects.filter(shop=shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop=shop)
    try:
        about = About.objects.filter(shop=shop).get()
    except:
        about = Page(shop=shop)
        about.save()
    form = AboutForm(request.POST or None, instance=about)
    if form.is_valid():
        form.save()
        request.flash['message'] = unicode(_("Page successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('page_edit_about'))
    return render_to_response('store_admin/web_store/pages_edit_about.html',
                              {'form': form, 'static_pages': static_pages, 'dynamic_pages': dynamic_pages},
                              RequestContext(request))    


@shop_admin_required
def blog_pages(request):
    shop = request.shop
    about = About.objects.filter(shop=shop).get()
    home = Home.objects.filter(shop=shop).get()
    pages = Page.objects.filter(shop=shop)
    posts = Post.objects.filter(shop=shop).filter(draft=False)
    drafts = Post.objects.filter(shop=shop).filter(draft=True)
    return render_to_response('blog_pages/blog_pages.html', 
                              {'about': about,
                               'home': home,
                               'pages': pages,
                               'posts': posts,
                               'drafts': drafts,
                               },
                              RequestContext(request))

#@add_page_feature_enabled
@shop_admin_required    
def page_create(request):
    shop = request.shop
    static_pages = Page.objects.filter(shop=shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop=shop)
    form = PageForm(shop, request.POST or None)
    if form.is_valid():
        page = form.save(commit = False)
        page.shop = shop
        page.save()
        request.flash['message'] = unicode(_("Page successfully saved."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('web_store_pages'))
    
    return render_to_response('store_admin/web_store/pages_page_create.html',
                              {
                               'form': form,
                               'static_pages': static_pages,
                               'dynamic_pages': dynamic_pages,
                               },
                              RequestContext(request))    

@shop_admin_required    
def page_revert(request, id):
    version = get_object_or_404(PageVersion, pk=id)
    shop = request.shop
    if version.page.shop != shop:
        raise Http404
    
    page = version.page
    page.name = version.name 
    page.name_link = version.name_link
    page.title = version.title
    page.body = version.body
    page.meta_content = version.meta_content
    page.save()
    
    #version.delete()
    
    request.flash['message'] = unicode(_("Page successfully recovered."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('page_edit_static', args=[page.id]))

@shop_admin_required    
def page_version_delete(request, id):
    version = get_object_or_404(PageVersion, pk=id)
    shop = request.shop
    if version.page.shop != shop:
        raise Http404
    
    page_id = version.page.id    
    version.delete()
    
    request.flash['message'] = unicode(_("Page version successfully recovered."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('page_edit_static', args=[page_id]))

@shop_admin_required
def page_edit_static(request, id):
    shop = request.shop
    
    page = get_object_or_404(Page, pk=id)
    page_name = page.name
    page_name_link = page.name_link
    page_title = page.title
    page_body = page.body
    page_meta_content = page.meta_content
    
    static_pages = Page.objects.filter(shop=shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop=shop)
    form = PageForm(shop, request.POST or None, instance=page)
    if request.method == "POST":
        if form.is_valid():            
            new_page = form.save(commit = False)
            new_page.save()
            version = PageVersion(page=page)
            version.name = page_name
            version.name_link = page_name_link
            version.title = page_title
            version.body = page_body
            version.meta_content = page_meta_content
            version.save()
            request.flash['message'] = unicode(_("Page successfully edited."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('page_edit_static', args=[id]))
        
    return render_to_response('store_admin/web_store/pages_edit_static_page.html', {
                                       'form': form,
                                       'page': page,
                                       'static_pages': static_pages, 
                                       'dynamic_pages': dynamic_pages
                                       },
                                      RequestContext(request))
        
    
@shop_admin_required    
def page_edit_dynamic(request, id):
    page = get_object_or_404(DynamicPageContent, pk=id)
    shop = request.shop
    static_pages = Page.objects.filter(shop=shop)
    dynamic_pages = DynamicPageContent.objects.filter(shop=shop)
    form = DynamicPageForm(shop, request.POST or None, instance=page)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            request.flash['message'] = unicode(_("Page successfully edited."))
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('page_edit_dynamic', args=[id]))
        
    return render_to_response('store_admin/web_store/pages_edit_dynamic_page.html',
                                  {
                                   'form': form,
                                   'page': page,
                                   'static_pages': static_pages, 
                                   'dynamic_pages': dynamic_pages
                                   },
                                  RequestContext(request))


@shop_admin_required    
def page_delete(request, id):
    page = get_object_or_404(Page, pk=id)
    shop = request.shop
    if page.shop != shop:
        raise Http404
    page.delete()
    request.flash['message'] = unicode(_("Page successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('web_store_pages'))    


@shop_admin_required
def navigation(request):
    shop = request.shop
    menus = Menu.objects.filter(shop=shop)
    link_form = LinkForm(shop, request.POST or None)
    return render_to_response('store_admin/web_store/navigation.html', 
                              {'menus': menus, 'link_form': link_form},
                              RequestContext(request))    


#@shop_admin_required    
#def link_add(request, id):
#    menu = get_object_or_404(Menu, pk=id)
#    shop = request.shop
#    if menu.shop != shop:
#        raise Http404
#    form = LinkForm(shop, request.POST or None)
#    if form.is_valid():
#        link = form.save(commit = False)
#        link.menu = menu
#        link.order = menu.links().count() + 1 
#        link.save()
#        request.flash['message'] = unicode(_("Link successfully saved."))
#        request.flash['severity'] = "success"
#        return HttpResponseRedirect(reverse('web_store_navigation'))
#    return render_to_response('store_admin/web_store/navigation_add_link.html',
#                              {'form': form,
#                               'menu': menu},
#                              RequestContext(request))

@shop_admin_required    
def link_add2(request, id):
    menu = get_object_or_404(Menu, pk=id)
    shop = request.shop
    if menu.shop != shop:
        raise Http404
    
    if request.method == "POST":
        form = LinkForm(shop, request.POST or None)
        if form.is_valid():
            link = form.save(commit = False)
            link.menu = menu
            link.order = menu.links().count() + 1 
            link.save()
            request.flash['message'] = unicode(_("Link successfully saved."))
            request.flash['severity'] = "success"            
        else:
            request.flash['message'] = unicode(_("Could not save link, all fields are required"))
            request.flash['severity'] = "error"
            
        return HttpResponseRedirect(reverse('web_store_navigation'))
    
    raise Http404
    

@shop_admin_required    
def link_edit(request, id):
    link = get_object_or_404(Link, pk=id)
    shop = request.shop
    if link.menu.shop != shop:
        raise Http404
    form = LinkForm(shop, request.POST or None, instance=link)
    if form.is_valid():
        form.save()
        request.flash['message'] = unicode(_("Link successfully edited."))
        request.flash['severity'] = "success"
        return HttpResponseRedirect(reverse('link_edit', args=[id]))
    return render_to_response('store_admin/web_store/navigation_edit_link.html',
                              {'form': form,
                               'link': link},
                              RequestContext(request))


@shop_admin_required    
def link_delete(request, id):
    link = get_object_or_404(Link, pk=id)
    shop = request.shop
    if link.menu.shop != shop:
        raise Http404
    link.delete()
    request.flash['message'] = unicode(_("Link successfully deleted."))
    request.flash['severity'] = "success"
    return HttpResponseRedirect(reverse('web_store_navigation'))



def link_order(request):
    name_menu = request.GET.get('name')
    ids = request.GET.getlist(name_menu+'[]')
    print name_menu
    print ids
    for i, id in enumerate(ids):
        link = Link.objects.get(id=id)
        link.order = i 
        link.save()
    return HttpResponse("")
    