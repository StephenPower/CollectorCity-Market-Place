from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template import loader
from django.http import HttpResponse
from bidding.views import my_render

def success(request):
    return HttpResponse(my_render(request, {}, 'payment_success'))

def cancel(request):
    return HttpResponse(my_render(request, {}, 'payment_cancel'))