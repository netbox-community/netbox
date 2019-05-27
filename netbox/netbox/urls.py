from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

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
    path(r'', HomeView.as_view(), name='home'),
    path(r'search/', SearchView.as_view(), name='search'),

    # Login/logout
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),

    # Apps
    path(r'circuits/', include('circuits.urls')),
    path(r'dcim/', include('dcim.urls')),
    path(r'extras/', include('extras.urls')),
    path(r'ipam/', include('ipam.urls')),
    path(r'secrets/', include('secrets.urls')),
    path(r'tenancy/', include('tenancy.urls')),
    path(r'user/', include('users.urls')),
    path(r'virtualization/', include('virtualization.urls')),

    # API
    path(r'api/', APIRootView.as_view(), name='api-root'),
    path(r'api/circuits/', include('circuits.api.urls')),
    path(r'api/dcim/', include('dcim.api.urls')),
    path(r'api/extras/', include('extras.api.urls')),
    path(r'api/ipam/', include('ipam.api.urls')),
    path(r'api/secrets/', include('secrets.api.urls')),
    path(r'api/tenancy/', include('tenancy.api.urls')),
    path(r'api/virtualization/', include('virtualization.api.urls')),
    path(r'api/docs/', schema_view.with_ui('swagger'), name='api_docs'),
    path(r'api/redoc/', schema_view.with_ui('redoc'), name='api_redocs'),
    re_path(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(), name='schema_swagger'),

    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    path(r'media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),

    # Admin
    path(r'admin/', admin_site.urls),

]

if settings.WEBHOOKS_ENABLED:
    _patterns += [
        path(r'admin/webhook-backend-status/', include('django_rq.urls')),
    ]

if settings.DEBUG:
    import debug_toolbar
    _patterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]

# Prepend BASE_PATH
urlpatterns = [
    path(r'{}'.format(settings.BASE_PATH), include(_patterns))
]

handler500 = 'utilities.views.server_error'
