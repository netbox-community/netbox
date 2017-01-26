from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView

from . import views


router = routers.DefaultRouter()
router.register(r'sites', views.SiteViewSet)
router.register(r'rack-groups', views.RackGroupViewSet)
router.register(r'rack-roles', views.RackRoleViewSet)
router.register(r'racks', views.RackViewSet)
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'device-types', views.DeviceTypeViewSet)
router.register(r'device-roles', views.DeviceRoleViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'devices', views.DeviceViewSet)
router.register(r'interface-connections', views.InterfaceConnectionViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Sites
    url(r'^sites/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_SITE}, name='site_graphs'),

    # Racks
    url(r'^racks/(?P<pk>\d+)/rack-units/$', views.RackUnitListView.as_view(), name='rack_units'),

    # Device types
    # TODO: Nested DeviceType components

    # Devices
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', views.LLDPNeighborsView.as_view(), name='device_lldp-neighbors'),
    url(r'^devices/(?P<pk>\d+)/console-ports/$', views.NestedConsolePortViewSet.as_view({'get': 'list'}), name='device_consoleports'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/$', views.NestedConsoleServerPortViewSet.as_view({'get': 'list'}), name='device_consoleserverports'),
    url(r'^devices/(?P<pk>\d+)/power-ports/$', views.NestedPowerPortViewSet.as_view({'get': 'list'}), name='device_powerports'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/$', views.NestedPowerOutletViewSet.as_view({'get': 'list'}), name='device_poweroutlets'),
    url(r'^devices/(?P<pk>\d+)/interfaces/$', views.NestedInterfaceViewSet.as_view({'get': 'list'}), name='device_interfaces'),
    url(r'^devices/(?P<pk>\d+)/device-bays/$', views.NestedDeviceBayViewSet.as_view({'get': 'list'}), name='device_devicebays'),
    url(r'^devices/(?P<pk>\d+)/modules/$', views.NestedModuleViewSet.as_view({'get': 'list'}), name='device_modules'),
    # TODO: Services

    # Console ports
    url(r'^console-ports/(?P<pk>\d+)/$', views.ConsolePortViewSet.as_view({'get': 'retrieve'}), name='consoleport'),

    # Console server ports
    url(r'^console-server-ports/(?P<pk>\d+)/$', views.ConsoleServerPortViewSet.as_view({'get': 'retrieve'}), name='consoleserverport'),

    # Power ports
    url(r'^power-ports/(?P<pk>\d+)/$', views.PowerPortViewSet.as_view({'get': 'retrieve'}), name='powerport'),

    # Power outlets
    url(r'^power-outlets/(?P<pk>\d+)/$', views.PowerOutletViewSet.as_view({'get': 'retrieve'}), name='poweroutlet'),

    # Interfaces
    url(r'^interfaces/(?P<pk>\d+)/$', views.InterfaceViewSet.as_view({'get': 'retrieve'}), name='interface'),
    url(r'^interfaces/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_INTERFACE},
        name='interface_graphs'),

    # Device bays
    url(r'^device-bays/(?P<pk>\d+)/$', views.DeviceBayViewSet.as_view({'get': 'retrieve'}), name='devicebay'),

    # Modules
    url(r'^modules/(?P<pk>\d+)/$', views.ModuleViewSet.as_view({'get': 'retrieve'}), name='module'),

    # Miscellaneous
    url(r'^related-connections/$', views.RelatedConnectionsView.as_view(), name='related_connections'),
    url(r'^topology-maps/(?P<slug>[\w-]+)/$', TopologyMapView.as_view(), name='topology_map'),

]
