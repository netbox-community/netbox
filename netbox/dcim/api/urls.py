from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView

from .views import (

    # Viewsets
    ConsolePortViewSet, ConsoleServerPortViewSet, DeviceViewSet, DeviceBayViewSet, DeviceRoleViewSet, DeviceTypeViewSet,
    InterfaceViewSet, ManufacturerViewSet, ModuleViewSet, PlatformViewSet, PowerPortViewSet, PowerOutletViewSet,
    RackViewSet, RackGroupViewSet, RackRoleViewSet, SiteViewSet,

    # Legacy views
    ConsolePortView, InterfaceConnectionView, InterfaceConnectionListView, InterfaceDetailView, PowerPortView,
    LLDPNeighborsView, RackUnitListView, RelatedConnectionsView,
)


router = routers.DefaultRouter()
router.register(r'sites', SiteViewSet)
router.register(r'rack-groups', RackGroupViewSet)
router.register(r'rack-roles', RackRoleViewSet)
router.register(r'racks', RackViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'device-types', DeviceTypeViewSet)
router.register(r'device-roles', DeviceRoleViewSet)
router.register(r'platforms', PlatformViewSet)
router.register(r'devices', DeviceViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Sites
    url(r'^sites/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_SITE}, name='site_graphs'),

    # Racks
    url(r'^racks/(?P<pk>\d+)/rack-units/$', RackUnitListView.as_view(), name='rack_units'),

    # Devices
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', LLDPNeighborsView.as_view(), name='device_lldp-neighbors'),
    url(r'^devices/(?P<pk>\d+)/console-ports/$', ConsolePortViewSet.as_view({'get': 'list'}), name='device_consoleports'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/$', ConsoleServerPortViewSet.as_view({'get': 'list'}), name='device_consoleserverports'),
    url(r'^devices/(?P<pk>\d+)/power-ports/$', PowerPortViewSet.as_view({'get': 'list'}), name='device_powerports'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/$', PowerOutletViewSet.as_view({'get': 'list'}), name='device_poweroutlets'),
    url(r'^devices/(?P<pk>\d+)/interfaces/$', InterfaceViewSet.as_view({'get': 'list'}), name='device_interfaces'),
    url(r'^devices/(?P<pk>\d+)/device-bays/$', DeviceBayViewSet.as_view({'get': 'list'}), name='device_devicebays'),
    url(r'^devices/(?P<pk>\d+)/modules/$', ModuleViewSet.as_view({'get': 'list'}), name='device_modules'),
    # TODO: Services

    # Console ports
    url(r'^console-ports/(?P<pk>\d+)/$', ConsolePortView.as_view(), name='consoleport'),

    # Power ports
    url(r'^power-ports/(?P<pk>\d+)/$', PowerPortView.as_view(), name='powerport'),

    # Interfaces
    url(r'^interfaces/(?P<pk>\d+)/$', InterfaceDetailView.as_view(), name='interface_detail'),
    url(r'^interfaces/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_INTERFACE},
        name='interface_graphs'),
    url(r'^interface-connections/$', InterfaceConnectionListView.as_view(), name='interfaceconnection_list'),
    url(r'^interface-connections/(?P<pk>\d+)/$', InterfaceConnectionView.as_view(), name='interfaceconnection_detail'),

    # Miscellaneous
    url(r'^related-connections/$', RelatedConnectionsView.as_view(), name='related_connections'),
    url(r'^topology-maps/(?P<slug>[\w-]+)/$', TopologyMapView.as_view(), name='topology_map'),

]
