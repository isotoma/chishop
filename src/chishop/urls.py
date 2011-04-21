# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include, handler404, handler500
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('')

# Serve static pages.
if settings.SERVE_MEDIA:
    urlpatterns += patterns("django.views",
        url(r"^%s(?P<path>.*)$" % settings.MEDIA_URL[1:], "static.serve", {
            "document_root": settings.MEDIA_ROOT}))

urlpatterns += patterns("",
    # Admin interface
    url(r'^admin/doc/', include("django.contrib.admindocs.urls")),
    url(r'^admin/', include(admin.site.urls)),

    # Registration
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^search/', 'haystack.views.basic_search', {
        'template': 'djangopypi/search_results.html',
    }, name='haystack_search'),

    # The Chishop
    url(r'', include("djangopypi.urls")),
)
