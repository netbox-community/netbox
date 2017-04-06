from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from netbox.views import APIRootView, home, handle_500, SearchView, trigger_500
from users.views import login, logout


handler500 = handle_500
swagger_view = get_swagger_view(title='NetBox API')

_patterns = [

    # Base views
    url(r'^$', home, name='home'),
    url(r'^search/$', SearchView.as_view(), name='search'),

    # Login/logout
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    # Apps
    url(r'^circuits/', include('circuits.urls')),
    url(r'^dcim/', include('dcim.urls')),
    url(r'^extras/', include('extras.urls')),
    url(r'^ipam/', include('ipam.urls')),
    url(r'^secrets/', include('secrets.urls')),
    url(r'^tenancy/', include('tenancy.urls')),
    url(r'^user/', include('users.urls')),

    # API
    url(r'^api/$', APIRootView.as_view(), name='api-root'),
    url(r'^api/circuits/', include('circuits.api.urls')),
    url(r'^api/dcim/', include('dcim.api.urls')),
    url(r'^api/extras/', include('extras.api.urls')),
    url(r'^api/ipam/', include('ipam.api.urls')),
    url(r'^api/secrets/', include('secrets.api.urls')),
    url(r'^api/tenancy/', include('tenancy.api.urls')),
    url(r'^api/docs/', swagger_view, name='api_docs'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Error testing
    url(r'^500/$', trigger_500),

    # Admin
    url(r'^admin/', admin.site.urls),

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
