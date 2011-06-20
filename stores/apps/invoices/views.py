from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from core.decorators import staff_required

import datetime