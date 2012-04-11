#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the default wsgi file for the POC project. It's used by Apache's
mod_wsgi to start the application."""

import os
import sys

wsgi_path = os.path.abspath(os.path.dirname(__file__))
# guessing that this .wsgi file is under project/deploy/ directory
sys.path.append(os.path.join(wsgi_path, "../env/lib/python2.6/site-packages/"))
sys.path.append(os.path.join(wsgi_path, ".."))
#sys.path.append(os.path.join(wsgi_path, "../../"))
#sys.path.append(os.path.join(wsgi_path, "../apps/"))

# we need to setup the DJANGO_SETTINGS_MODULE before doing any import form the
# django.* namespace:
os.environ["DJANGO_SETTINGS_MODULE"] = "marketplaces.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
