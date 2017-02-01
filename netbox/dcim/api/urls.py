from django.conf.urls import include, url

from rest_framework import routers

from extras.api.views import TopologyMapView
from ipam.api.views import ServiceViewSet
from . import views


router = routers.DefaultRouter()

# Sites
router.register(r'sites', views.SiteViewSet)

# Racks
router.register(r'rack-groups', views.RackGroupViewSet)
router.register(r'rack-roles', views.RackRoleViewSet)
router.register(r'racks', views.RackViewSet)

# Device types
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'device-types', views.DeviceTypeViewSet)

# TODO: Device type components

# Devices
router.register(r'device-roles', views.DeviceRoleViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'devices', views.DeviceViewSet)

# Device components
router.register(r'console-ports', views.ConsolePortViewSet)
router.register(r'console-server-ports', views.ConsoleServerPortViewSet)
router.register(r'power-ports', views.PowerPortViewSet)
router.register(r'power-outlets', views.PowerOutletViewSet)
router.register(r'interfaces', views.InterfaceViewSet)
router.register(r'device-bays', views.DeviceBayViewSet)
router.register(r'modules', views.ModuleViewSet)
router.register(r'services', ServiceViewSet)

# Interface connections
router.register(r'interface-connections', views.InterfaceConnectionViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Miscellaneous
    url(r'^related-connections/$', views.RelatedConnectionsView.as_view(), name='related_connections'),
    url(r'^topology-maps/(?P<slug>[\w-]+)/$', TopologyMapView.as_view(), name='topology_map'),

]
