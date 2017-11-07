from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
from rest_framework_swagger.views import get_swagger_view

from netbox.views import APIRootView, HomeView, SearchView
from users.views import LoginView, LogoutView

swagger_view = get_swagger_view(title='NetBox API')

_patterns = [

    # Base views
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^search/$', SearchView.as_view(), name='search'),

    # Login/logout
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    # Apps
    url(r'^circuits/', include('circuits.urls')),
    url(r'^dcim/', include('dcim.urls')),
    url(r'^extras/', include('extras.urls')),
    url(r'^ipam/', include('ipam.urls')),
    url(r'^secrets/', include('secrets.urls')),
    url(r'^tenancy/', include('tenancy.urls')),
    url(r'^user/', include('users.urls')),
    url(r'^virtualization/', include('virtualization.urls')),

    # API
    url(r'^api/$', APIRootView.as_view(), name='api-root'),
    url(r'^api/circuits/', include('circuits.api.urls')),
    url(r'^api/dcim/', include('dcim.api.urls')),
    url(r'^api/extras/', include('extras.api.urls')),
    url(r'^api/ipam/', include('ipam.api.urls')),
    url(r'^api/secrets/', include('secrets.api.urls')),
    url(r'^api/tenancy/', include('tenancy.api.urls')),
    url(r'^api/virtualization/', include('virtualization.api.urls')),
    url(r'^api/docs/', swagger_view, name='api_docs'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

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
