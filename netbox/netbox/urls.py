from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from netbox.views import APIRootView, home, handle_500, SearchView, trigger_500
from users.views import login, logout


handler500 = handle_500

_patterns = [

    # Base views
    url(r'^$', home, name='home'),
    url(r'^search/$', SearchView.as_view(), name='search'),

    # Login/logout
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    # Apps
    url(r'^circuits/', include('circuits.urls', namespace='circuits')),
    url(r'^dcim/', include('dcim.urls', namespace='dcim')),
    url(r'^extras/', include('extras.urls', namespace='extras')),
    url(r'^ipam/', include('ipam.urls', namespace='ipam')),
    url(r'^secrets/', include('secrets.urls', namespace='secrets')),
    url(r'^tenancy/', include('tenancy.urls', namespace='tenancy')),
    url(r'^user/', include('users.urls', namespace='user')),

    # API
    url(r'^api/$', APIRootView.as_view(), name='api-root'),
    url(r'^api/circuits/', include('circuits.api.urls', namespace='circuits-api')),
    url(r'^api/dcim/', include('dcim.api.urls', namespace='dcim-api')),
    url(r'^api/extras/', include('extras.api.urls', namespace='extras-api')),
    url(r'^api/ipam/', include('ipam.api.urls', namespace='ipam-api')),
    url(r'^api/secrets/', include('secrets.api.urls', namespace='secrets-api')),
    url(r'^api/tenancy/', include('tenancy.api.urls', namespace='tenancy-api')),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Error testing
    url(r'^500/$', trigger_500),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

]

if settings.DEBUG:
    import debug_toolbar
    _patterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# Prepend BASE_PATH
urlpatterns = [
    url(r'^{}'.format(settings.BASE_PATH), include(_patterns))
]
