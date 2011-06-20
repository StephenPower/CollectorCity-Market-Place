import datetime
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response #, get_object_or_404
from django.template import loader
from django.utils.translation import ugettext as _

#from django.core.paginator import Paginator, InvalidPage, EmptyPage

from auth.models import User
from bidding.views import my_render
from core.decorators import shop_required
from sell.models import Cart

from forms import BidderForm
from models import Profile, EmailVerify

@shop_required
def register(request):
    #TODO: transaction
    form = BidderForm(request, request.POST or None)
    if form.is_valid():
        #Generate user
        user = User.objects.create_user(form.cleaned_data["username"],
                                        form.cleaned_data["email"], 
                                        form.cleaned_data["password1"])
#        user.first_name = form.cleaned_data["first_name"]
#        user.last_name = form.cleaned_data["last_name"]
#        user.is_active = False
        
        
        user.save()
        
#        """ Set cart """
#        cart = Cart(bidder=user)
#        cart.save()
        
        """ Set profile """
        profile = Profile(user=user)
        
#        profile.street_address = form.cleaned_data["street_address"]
#        profile.city = form.cleaned_data["city"]
#        profile.state = form.cleaned_data["state"]
#        profile.zip = form.cleaned_data["zip"]
#        profile.country = form.cleaned_data["country"]
#        profile.phone = form.cleaned_data["phone"]
#        profile.photo = form.cleaned_data["photo"]
#        profile.birth = datetime.date(
#                      int(form.cleaned_data['year']),
#                      int(form.cleaned_data['month']),
#                      int(form.cleaned_data['day']),
#                      )

        profile.save()

        """ Send mail to confirm account """
        email_verify = EmailVerify(user=user, user_activation=True)
        code = email_verify.generate_code()
        email_verify.save()
        
                              
        #send_mail_account_confirmation(user, email_verify.code, request.shop.name_shop(), request.get_host())        

        return HttpResponseRedirect(reverse('confirmemail', args=[code]))
                    
        #return HttpResponseRedirect(reverse('welcome'))
    
    print form.errors
    
    t = loader.get_template('users/blocks/register.html')
    c = RequestContext(request, {'form': form})
    block_register = (t.render(c))
    return HttpResponse(my_render(request, {'register': block_register,
                                         'page_title': 'Register',
                                         'page_description': 'Register' 
                                         }, 'register'))
    
#    return render_to_response('users/register.html', 
#                              {'form': form},
#                              RequestContext(request))



def send_mail_account_confirmation(user, code, shop_name, site_url):
    """
        Send message to the user to confirm your account
    """
    link = "http://%s/users/confirmemail/%s/" % (site_url , code)
    
    subject = "%s Account Confirmation" % shop_name
    
    
    
    text_content = _("""
    Hi %(first_name)s %(last_name)s,
    
    You recently registered for %(shop_name)s. Please confirm your account by clicking this link:
    %(link)s
                       
    Thanks.
                       
    %(shop_name)s Team.""") % {'first_name': user.first_name, 'last_name': user.last_name, 'link': link, 'shop_name': shop_name} 
    
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [user.email, settings.EMAIL_FROM])
    try:
        msg.send()
    except:
        logging.exception("failure sending mail")
        
        
def confirmemail(request, code):
    try:
        verify = EmailVerify.objects.filter(code = code).get()
        if not verify.user_activation:
            request.flash['message'] = _("Account verification failed")
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('welcome'))
        else:
            user = verify.user
            user.is_active = True
            user.save()
            verify.delete()
            
            from auth import load_backend, login
            if not hasattr(user, 'backend'):
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.pk):
                        user.backend = backend
                        break
            if hasattr(user, 'backend'):
                login(request, user)

            request.flash['message'] = unicode(_("Welcome, you are register now."))
            request.flash['severity'] = "success"

            return HttpResponseRedirect('/')
#            return render_to_response('users/welcome.html', {},
#                                      RequestContext(request))
    except EmailVerify.DoesNotExist:
        request.flash['message'] = _("Account verification failed")
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('welcome'))


@shop_required
def welcome(request):
    #def welcome(request, template_name='users/welcome.html'):
#    t = loader.get_template('users/blocks/welcome.html')
#    c = RequestContext(request, {})
#    block_welcome = (t.render(c))
    return HttpResponse(my_render(request, {'name_shop': request.shop.name_shop,
                                            'page_title': 'Welcome',
                                            'page_description': 'Welcome',                                          
                                           }, 'welcome'))

    #return render_to_response(template_name,{},RequestContext(request))


@shop_required
def re_send_mail(request, user_id):
    """
        re-send the email verification email 
    """
    user = User.objects.get(pk=user_id)
    try:
        verify = EmailVerify.objects.filter(user = user).get()
        verify.delete()
    except EmailVerify.DoesNotExist:
        pass
    email_verify = EmailVerify(user=user, user_activation=True)
    email_verify.generate_code()
    email_verify.save()
    send_mail_account_confirmation(user, email_verify.code, request.shop.name_shop(), request.get_host())        
    return HttpResponseRedirect(reverse('welcome'))        
