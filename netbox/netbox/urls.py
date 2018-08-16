from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.views.static import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from netbox.views import APIRootView, HomeView, SearchView
from users.views import LoginView, LogoutView
from .admin import admin_site

schema_view = get_schema_view(
    openapi.Info(
        title="NetBox API",
        default_version='v2',
        description="API to access NetBox",
        terms_of_service="https://github.com/digitalocean/netbox",
        contact=openapi.Contact(email="netbox@digitalocean.com"),
        license=openapi.License(name="Apache v2 License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
)

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
    url(r'^api/docs/$', schema_view.with_ui('swagger'), name='api_docs'),
    url(r'^api/redoc/$', schema_view.with_ui('redoc'), name='api_redocs'),
    url(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(), name='schema_swagger'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Admin
    url(r'^admin/', admin_site.urls),

]

if settings.WEBHOOKS_ENABLED:
    _patterns += [
        url(r'^admin/webhook-backend-status/', include('django_rq.urls')),
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

handler500 = 'utilities.views.server_error'
