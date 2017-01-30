from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView
from ipam.api.views import ServiceViewSet, DeviceServiceViewSet

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

# Devices
router.register(r'device-roles', views.DeviceRoleViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'devices', views.DeviceViewSet)
router.register(r'console-ports', views.ConsolePortViewSet)
router.register(r'console-server-ports', views.ConsoleServerPortViewSet)
router.register(r'power-ports', views.PowerPortViewSet)
router.register(r'power-outlets', views.PowerOutletViewSet)
router.register(r'interfaces', views.InterfaceViewSet)
router.register(r'interface-connections', views.InterfaceConnectionViewSet)
router.register(r'device-bays', views.DeviceBayViewSet)
router.register(r'modules', views.ModuleViewSet)
router.register(r'services', ServiceViewSet)

# Device components
device_router = routers.DefaultRouter()
device_router.register(r'console-ports', views.DeviceConsolePortViewSet, base_name='consoleport')
device_router.register(r'console-server-ports', views.DeviceConsoleServerPortViewSet, base_name='consoleserverport')
device_router.register(r'power-ports', views.DevicePowerPortViewSet, base_name='powerport')
device_router.register(r'power-outlets', views.DevicePowerOutletViewSet, base_name='poweroutlet')
device_router.register(r'interfaces', views.DeviceInterfaceViewSet, base_name='interface')
device_router.register(r'device-bays', views.DeviceDeviceBayViewSet, base_name='devicebay')
device_router.register(r'modules', views.DeviceModuleViewSet, base_name='module')
device_router.register(r'services', DeviceServiceViewSet, base_name='service')

urlpatterns = [

    url(r'', include(router.urls)),
    url(r'^devices/(?P<pk>\d+)/', include(device_router.urls)),

    # Sites
    url(r'^sites/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_SITE}, name='site_graphs'),

    # Racks
    url(r'^racks/(?P<pk>\d+)/rack-units/$', views.RackUnitListView.as_view(), name='rack_units'),

    # Device types
    # TODO: Nested DeviceType components

    # Devices
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', views.LLDPNeighborsView.as_view(), name='device_lldp-neighbors'),

    # Interfaces
    url(r'^interfaces/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_INTERFACE},
        name='interface_graphs'),

    # Miscellaneous
    url(r'^related-connections/$', views.RelatedConnectionsView.as_view(), name='related_connections'),
    url(r'^topology-maps/(?P<slug>[\w-]+)/$', TopologyMapView.as_view(), name='topology_map'),

]
