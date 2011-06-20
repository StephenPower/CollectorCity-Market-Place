from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auth.models import User


def home(request):
    from bidding.views import bidding_home
    if request.shop:
        return bidding_home(request)
    elif hasattr(request, 'marketplace') and request.marketplace:
        return HttpResponseRedirect("http://%s" % request.marketplace.base_domain)
    
    return render_to_response('core/home.html', {}, 
                              RequestContext(request)) 


def redirect(request):
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('shop_list'))
    elif request.shop and request.user == request.shop.admin:    
        return HttpResponseRedirect(reverse('home_admin'))
    else:
        return HttpResponseRedirect(reverse('home'))


#delete this
def admin_login(request, user_id):
    user = User.objects.get(id=user_id)
    from auth import load_backend, login
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        login(request, user)
    return HttpResponseRedirect('/')


def remove_qa_user(request):
    try:
        user = User.objects.filter(username="qatester").get()
        user.delete()
    except User.DoesNotExist:
        return HttpResponse(404)
    except Exception, e:
        return HttpResponse(500)
    return HttpResponse(status=200)