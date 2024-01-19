from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from account.views import LoginView, LogoutView
from netbox.api.views import APIRootView, StatusView
from netbox.graphql.schema import schema
from netbox.graphql.views import GraphQLView
from netbox.plugins.urls import plugin_patterns, plugin_api_patterns
from netbox.views import HomeView, StaticMediaFailureView, SearchView, htmx
from .admin import admin_site

_patterns = [

    # Base views
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),

    # Login/logout
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),

    # Apps
    path('circuits/', include('circuits.urls')),
    path('core/', include('core.urls')),
    path('dcim/', include('dcim.urls')),
    path('extras/', include('extras.urls')),
    path('ipam/', include('ipam.urls')),
    path('tenancy/', include('tenancy.urls')),
    path('users/', include('users.urls')),
    path('virtualization/', include('virtualization.urls')),
    path('vpn/', include('vpn.urls')),
    path('wireless/', include('wireless.urls')),

    # Current user views
    path('user/', include('account.urls')),

    # HTMX views
    path('htmx/object-selector/', htmx.ObjectSelectorView.as_view(), name='htmx_object_selector'),

    # API
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/circuits/', include('circuits.api.urls')),
    path('api/core/', include('core.api.urls')),
    path('api/dcim/', include('dcim.api.urls')),
    path('api/extras/', include('extras.api.urls')),
    path('api/ipam/', include('ipam.api.urls')),
    path('api/tenancy/', include('tenancy.api.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/virtualization/', include('virtualization.api.urls')),
    path('api/vpn/', include('vpn.api.urls')),
    path('api/wireless/', include('wireless.api.urls')),
    path('api/status/', StatusView.as_view(), name='api-status'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='api_docs'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='api_redocs'),

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

handler404 = 'netbox.views.errors.handler_404'
handler500 = 'netbox.views.errors.handler_500'
