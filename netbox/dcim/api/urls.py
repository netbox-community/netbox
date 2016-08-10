from django.conf.urls import url

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView

from .views import *


urlpatterns = [

    # Sites
    url(r'^sites/$', SiteListView.as_view(), name='site_list'),
    url(r'^sites/(?P<pk>\d+)/$', SiteDetailView.as_view(), name='site_detail'),
    url(r'^sites/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_SITE}, name='site_graphs'),
    url(r'^sites/(?P<site>\d+)/racks/$', RackListView.as_view(), name='site_racks'),

    # Rack groups
    url(r'^rack-groups/$', RackGroupListView.as_view(), name='rackgroup_list'),
    url(r'^rack-groups/(?P<pk>\d+)/$', RackGroupDetailView.as_view(), name='rackgroup_detail'),

    # Racks
    url(r'^racks/$', RackListView.as_view(), name='rack_list'),
    url(r'^racks/(?P<pk>\d+)/$', RackDetailView.as_view(), name='rack_detail'),
    url(r'^racks/(?P<pk>\d+)/rack-units/$', RackUnitListView.as_view(), name='rack_units'),

    # Manufacturers
    url(r'^manufacturers/$', ManufacturerListView.as_view(), name='manufacturer_list'),
    url(r'^manufacturers/(?P<pk>\d+)/$', ManufacturerDetailView.as_view(), name='manufacturer_detail'),

    # Device types
    url(r'^device-types/$', DeviceTypeListView.as_view(), name='devicetype_list'),
    url(r'^device-types/(?P<pk>\d+)/$', DeviceTypeDetailView.as_view(), name='devicetype_detail'),

    # Device roles
    url(r'^device-roles/$', DeviceRoleListView.as_view(), name='devicerole_list'),
    url(r'^device-roles/(?P<pk>\d+)/$', DeviceRoleDetailView.as_view(), name='devicerole_detail'),

    # Platforms
    url(r'^platforms/$', PlatformListView.as_view(), name='platform_list'),
    url(r'^platforms/(?P<pk>\d+)/$', PlatformDetailView.as_view(), name='platform_detail'),

    # Devices
    url(r'^devices/$', DeviceListView.as_view(), name='device_list'),
    url(r'^devices/(?P<pk>\d+)/$', DeviceDetailView.as_view(), name='device_detail'),
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', LLDPNeighborsView.as_view(), name='device_lldp-neighbors'),
    url(r'^devices/(?P<pk>\d+)/console-ports/$', ConsolePortListView.as_view(), name='device_consoleports'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/$', ConsoleServerPortListView.as_view(),
        name='device_consoleserverports'),
    url(r'^devices/(?P<pk>\d+)/power-ports/$', PowerPortListView.as_view(), name='device_powerports'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/$', PowerOutletListView.as_view(), name='device_poweroutlets'),
    url(r'^devices/(?P<pk>\d+)/interfaces/$', InterfaceListView.as_view(), name='device_interfaces'),
    url(r'^devices/(?P<pk>\d+)/device-bays/$', DeviceBayListView.as_view(), name='device_devicebays'),
    url(r'^devices/(?P<pk>\d+)/modules/$', ModuleListView.as_view(), name='device_modules'),

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
