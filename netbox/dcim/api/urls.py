from django.conf.urls import url

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView

from .views import *


urlpatterns = [

    # Sites
    url(r'^sites/$', SiteViewSet.as_view({'get': 'list'}), name='site_list'),
    url(r'^sites/(?P<pk>\d+)/$', SiteViewSet.as_view({'get': 'retrieve'}), name='site_detail'),
    url(r'^sites/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_SITE}, name='site_graphs'),

    # Rack groups
    url(r'^rack-groups/$', RackGroupViewSet.as_view({'get': 'list'}), name='rackgroup_list'),
    url(r'^rack-groups/(?P<pk>\d+)/$', RackGroupViewSet.as_view({'get': 'retrieve'}), name='rackgroup_detail'),

    # Rack roles
    url(r'^rack-roles/$', RackRoleViewSet.as_view({'get': 'list'}), name='rackrole_list'),
    url(r'^rack-roles/(?P<pk>\d+)/$', RackRoleViewSet.as_view({'get': 'retrieve'}), name='rackrole_detail'),

    # Racks
    url(r'^racks/$', RackViewSet.as_view({'get': 'list'}), name='rack_list'),
    url(r'^racks/(?P<pk>\d+)/$', RackViewSet.as_view({'get': 'retrieve'}), name='rack_detail'),
    url(r'^racks/(?P<pk>\d+)/rack-units/$', RackUnitListView.as_view(), name='rack_units'),

    # Manufacturers
    url(r'^manufacturers/$', ManufacturerViewSet.as_view({'get': 'list'}), name='manufacturer_list'),
    url(r'^manufacturers/(?P<pk>\d+)/$', ManufacturerViewSet.as_view({'get': 'retrieve'}), name='manufacturer_detail'),

    # Device types
    url(r'^device-types/$', DeviceTypeViewSet.as_view({'get': 'list'}), name='devicetype_list'),
    url(r'^device-types/(?P<pk>\d+)/$', DeviceTypeViewSet.as_view({'get': 'retrieve'}), name='devicetype_detail'),

    # Device roles
    url(r'^device-roles/$', DeviceRoleViewSet.as_view({'get': 'list'}), name='devicerole_list'),
    url(r'^device-roles/(?P<pk>\d+)/$', DeviceRoleViewSet.as_view({'get': 'retrieve'}), name='devicerole_detail'),

    # Platforms
    url(r'^platforms/$', PlatformViewSet.as_view({'get': 'list'}), name='platform_list'),
    url(r'^platforms/(?P<pk>\d+)/$', PlatformViewSet.as_view({'get': 'retrieve'}), name='platform_detail'),

    # Devices
    url(r'^devices/$', DeviceViewSet.as_view({'get': 'list'}), name='device_list'),
    url(r'^devices/(?P<pk>\d+)/$', DeviceViewSet.as_view({'get': 'retrieve'}), name='device_detail'),
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', LLDPNeighborsView.as_view(), name='device_lldp-neighbors'),
    url(r'^devices/(?P<pk>\d+)/console-ports/$', ConsolePortViewSet.as_view({'get': 'list'}), name='device_consoleports'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/$', ConsoleServerPortViewSet.as_view({'get': 'list'}), name='device_consoleserverports'),
    url(r'^devices/(?P<pk>\d+)/power-ports/$', PowerPortViewSet.as_view({'get': 'list'}), name='device_powerports'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/$', PowerOutletViewSet.as_view({'get': 'list'}), name='device_poweroutlets'),
    url(r'^devices/(?P<pk>\d+)/interfaces/$', InterfaceViewSet.as_view({'get': 'list'}), name='device_interfaces'),
    url(r'^devices/(?P<pk>\d+)/device-bays/$', DeviceBayViewSet.as_view({'get': 'list'}), name='device_devicebays'),
    url(r'^devices/(?P<pk>\d+)/modules/$', ModuleViewSet.as_view({'get': 'list'}), name='device_modules'),

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
