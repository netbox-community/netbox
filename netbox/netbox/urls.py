import importlib

from django.apps import apps
from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from netbox.views import APIRootView, HomeView, StaticMediaFailureView, SearchView
from users.views import LoginView, LogoutView
from .admin import admin_site

openapi_info = openapi.Info(
    title="NetBox API",
    default_version='v2',
    description="API to access NetBox",
    terms_of_service="https://github.com/netbox-community/netbox",
    license=openapi.License(name="Apache v2 License"),
)

schema_view = get_schema_view(
    openapi_info,
    validators=['flex', 'ssv'],
    public=True,
)

_patterns = [

    # Base views
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),

    # Login/logout
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Apps
    path('circuits/', include('circuits.urls')),
    path('dcim/', include('dcim.urls')),
    path('extras/', include('extras.urls')),
    path('ipam/', include('ipam.urls')),
    path('secrets/', include('secrets.urls')),
    path('tenancy/', include('tenancy.urls')),
    path('user/', include('users.urls')),
    path('virtualization/', include('virtualization.urls')),

    # API
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/circuits/', include('circuits.api.urls')),
    path('api/dcim/', include('dcim.api.urls')),
    path('api/extras/', include('extras.api.urls')),
    path('api/ipam/', include('ipam.api.urls')),
    path('api/secrets/', include('secrets.api.urls')),
    path('api/tenancy/', include('tenancy.api.urls')),
    path('api/virtualization/', include('virtualization.api.urls')),
    path('api/docs/', schema_view.with_ui('swagger'), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc'), name='api_redocs'),
    re_path(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(), name='schema_swagger'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),

    # Admin
    path('admin/', admin_site.urls),
    path('admin/webhook-backend-status/', include('django_rq.urls')),

    # Errors
    path('media-failure/', StaticMediaFailureView.as_view(), name='media_failure'),

]

# Plugins
plugin_patterns = []
plugin_api_patterns = []
for app in apps.get_app_configs():
    if hasattr(app, 'NetBoxPluginMeta'):
        if importlib.util.find_spec('{}.urls'.format(app.name)):
            urls = importlib.import_module('{}.urls'.format(app.name))
            url_slug = getattr(app.NetBoxPluginMeta, 'url_slug', app.label)
            if hasattr(urls, 'urlpatterns'):
                plugin_patterns.append(
                    path('{}/'.format(url_slug), include((urls.urlpatterns, app.label)))
                )
        if importlib.util.find_spec('{}.api'.format(app.name)):
            if importlib.util.find_spec('{}.api.urls'.format(app.name)):
                urls = importlib.import_module('{}.api.urls'.format(app.name))
                if hasattr(urls, 'urlpatterns'):
                    url_slug = getattr(app.NetBoxPluginMeta, 'url_slug', app.label)
                    plugin_api_patterns.append(
                        path('{}/'.format(url_slug), include((urls.urlpatterns, app.label)))
                    )

_patterns.append(
    path('plugins/', include((plugin_patterns, 'plugins')))
)
_patterns.append(
    path('api/plugins/', include((plugin_api_patterns, 'plugins-api')))
)

if settings.DEBUG:
    import debug_toolbar
    _patterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.METRICS_ENABLED:
    _patterns += [
        path('', include('django_prometheus.urls')),
    ]

# Prepend BASE_PATH
urlpatterns = [
    path('{}'.format(settings.BASE_PATH), include(_patterns))
]

handler500 = 'utilities.views.server_error'
