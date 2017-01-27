from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.api.views import GraphListView, TopologyMapView
from ipam.api.views import ChildServiceViewSet

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
    url(r'^devices/(?P<pk>\d+)/console-ports/$', views.ChildConsolePortViewSet.as_view({'get': 'list'}), name='consoleport-list'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/$', views.ChildConsoleServerPortViewSet.as_view({'get': 'list'}), name='consoleserverport-list'),
    url(r'^devices/(?P<pk>\d+)/power-ports/$', views.ChildPowerPortViewSet.as_view({'get': 'list'}), name='powerport-list'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/$', views.ChildPowerOutletViewSet.as_view({'get': 'list'}), name='poweroutlet-list'),
    url(r'^devices/(?P<pk>\d+)/interfaces/$', views.ChildInterfaceViewSet.as_view({'get': 'list'}), name='interface-list'),
    url(r'^devices/(?P<pk>\d+)/device-bays/$', views.ChildDeviceBayViewSet.as_view({'get': 'list'}), name='devicebay-list'),
    url(r'^devices/(?P<pk>\d+)/modules/$', views.ChildModuleViewSet.as_view({'get': 'list'}), name='module-list'),
    url(r'^devices/(?P<pk>\d+)/services/$', ChildServiceViewSet.as_view({'get': 'list'}), name='service-list'),

    # Console ports
    url(r'^console-ports/(?P<pk>\d+)/$', views.ConsolePortViewSet.as_view({'get': 'retrieve'}), name='consoleport-detail'),

    # Console server ports
    url(r'^console-server-ports/(?P<pk>\d+)/$', views.ConsoleServerPortViewSet.as_view({'get': 'retrieve'}), name='consoleserverport-detail'),

    # Power ports
    url(r'^power-ports/(?P<pk>\d+)/$', views.PowerPortViewSet.as_view({'get': 'retrieve'}), name='powerport-detail'),

    # Power outlets
    url(r'^power-outlets/(?P<pk>\d+)/$', views.PowerOutletViewSet.as_view({'get': 'retrieve'}), name='poweroutlet-detail'),

    # Interfaces
    url(r'^interfaces/(?P<pk>\d+)/$', views.InterfaceViewSet.as_view({'get': 'retrieve'}), name='interface-detail'),
    url(r'^interfaces/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_INTERFACE},
        name='interface_graphs'),

    # Device bays
    url(r'^device-bays/(?P<pk>\d+)/$', views.DeviceBayViewSet.as_view({'get': 'retrieve'}), name='devicebay-detail'),

    # Modules
    url(r'^modules/(?P<pk>\d+)/$', views.ModuleViewSet.as_view({'get': 'retrieve'}), name='module-detail'),

    # Miscellaneous
    url(r'^related-connections/$', views.RelatedConnectionsView.as_view(), name='related_connections'),
    url(r'^topology-maps/(?P<slug>[\w-]+)/$', TopologyMapView.as_view(), name='topology_map'),

]
