from django.conf.urls import patterns, include, url
from django.contrib import admin

from finance import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'balance.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)



# urlpatterns = patterns('',
#     # url(r'^$', 'finan.views.home', name='home'),
#     # url(r'^blog/', include('blog.urls')),

#     url(r'^$', views.index, name='index'),
#     # url(r'^control/', include('control.urls')),
#     # /control/5/
#     url(r'^(?P<control_id>\d+)/$', views.detail, name='detail'),
#     # /polls/5/results/
#     url(r'^(?P<control_id>\d+)/results/$', views.results, name='results'),
#     # /polls/5/vote/
#     url(r'^(?P<control_id>\d+)/vote/$', views.vote, name='vote'),
#     url(r'^admin/', include(admin.site.urls)),
# )
