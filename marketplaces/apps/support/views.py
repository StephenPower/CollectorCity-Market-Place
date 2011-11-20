from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from support.forms import FeaturesHelpTextForm
from support.models import FeaturesHelpText
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@staff_member_required
def admin_support(request):
    return render_to_response("admin/support.html", {}, RequestContext(request))

@staff_member_required
def admin_support_features(request):
    
    inst = None
    try:
        inst = FeaturesHelpText.objects.all()[0]
    except Exception:
        inst = FeaturesHelpText()
        inst.save()
        
    if request.method == "POST":
        form = FeaturesHelpTextForm(request.POST, instance=inst)
        if form.is_valid():
            help = form.save(commit=True)
            return HttpResponseRedirect(reverse("admin_support"))
    else:
        form = FeaturesHelpTextForm(instance=inst)
        
    params = {'form': form}
    return render_to_response("admin/help_text_features.html", params, RequestContext(request))