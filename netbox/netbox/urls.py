from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from extras.plugins.urls import plugin_admin_patterns, plugin_patterns, plugin_api_patterns
from netbox.api.views import APIRootView, StatusView
from netbox.graphql.schema import schema
from netbox.graphql.views import GraphQLView
from netbox.views import HomeView, StaticMediaFailureView, SearchView
from users.views import LoginView, LogoutView
from .admin import admin_site


openapi_info = openapi.Info(
    title="NetBox API",
    default_version='v3',
    description="API to access NetBox",
    terms_of_service="https://github.com/netbox-community/netbox",
    license=openapi.License(name="Apache v2 License"),
)

schema_view = get_schema_view(
    openapi_info,
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=()
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
    path('tenancy/', include('tenancy.urls')),
    path('user/', include('users.urls')),
    path('virtualization/', include('virtualization.urls')),

    # API
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/circuits/', include('circuits.api.urls')),
    path('api/dcim/', include('dcim.api.urls')),
    path('api/extras/', include('extras.api.urls')),
    path('api/ipam/', include('ipam.api.urls')),
    path('api/tenancy/', include('tenancy.api.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/virtualization/', include('virtualization.api.urls')),
    path('api/status/', StatusView.as_view(), name='api-status'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=86400), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=86400), name='api_redocs'),
    re_path(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=86400), name='schema_swagger'),

    # GraphQL
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)), name='graphql'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('media-failure/', StaticMediaFailureView.as_view(), name='media_failure'),

    # Plugins
    path('plugins/', include((plugin_patterns, 'plugins'))),
    path('api/plugins/', include((plugin_api_patterns, 'plugins-api'))),

    # Admin
    path('admin/background-tasks/', include('django_rq.urls')),
    path('admin/plugins/', include(plugin_admin_patterns)),
    path('admin/', admin_site.urls),
]


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

handler500 = 'netbox.views.server_error'
