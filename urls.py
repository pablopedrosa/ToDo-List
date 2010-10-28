from django.conf.urls.defaults import *
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

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
)