from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('pricing.views',
                       url(r'^$', 'index'),
                       url(r'^details/$', 'detail'),
                       url(r'^list/$', 'list'),
                       url(r'^export/$', 'export'),
                       url(r'^exportlist/$', 'exportlist'),
                       url(r'^DeleteEntry/$', 'delete_entry'),
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#     url(r'^admin/', include(admin.site.urls)),
)
