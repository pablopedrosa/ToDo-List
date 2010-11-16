from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin

import staticmedia

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^dbe/', include('dbe.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r"^item_action/(done|delete|onhold)/(\d*)/$", "todo.views.item_action"),
    (r'^admin/', include(admin.site.urls)),
    (r"^onhold_done/(onhold|done)/(yes|no)/(\d*)/$", "todo.views.onhold_done"),
    (r"^progress/(\d*)/$", "todo.views.progress"),
    (r"^logout/", "todo.views.mylogout"),
    (r'^signup', "todo.views.signup"),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    #(r'^$', direct_to_template, { 'template': 'index.html' }, 'index'),
    (r'^item/index/$', 'todo.views.itemindex'),
    (r'^graph/index/$', 'todo.views.barchart'),
    (r'^login/', 'todo.views.index'),
    (r'^$', 'todo.views.index'),
) + staticmedia.serve()