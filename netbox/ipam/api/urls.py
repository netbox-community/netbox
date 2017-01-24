from django.conf.urls import url

from .views import *


urlpatterns = [

    # VRFs
    url(r'^vrfs/$', VRFViewSet.as_view({'get': 'list'}), name='vrf_list'),
    url(r'^vrfs/(?P<pk>\d+)/$', VRFViewSet.as_view({'get': 'retrieve'}), name='vrf_detail'),

    # Roles
    url(r'^roles/$', RoleViewSet.as_view({'get': 'list'}), name='role_list'),
    url(r'^roles/(?P<pk>\d+)/$', RoleViewSet.as_view({'get': 'retrieve'}), name='role_detail'),

    # RIRs
    url(r'^rirs/$', RIRViewSet.as_view({'get': 'list'}), name='rir_list'),
    url(r'^rirs/(?P<pk>\d+)/$', RIRViewSet.as_view({'get': 'retrieve'}), name='rir_detail'),

    # Aggregates
    url(r'^aggregates/$', AggregateViewSet.as_view({'get': 'list'}), name='aggregate_list'),
    url(r'^aggregates/(?P<pk>\d+)/$', AggregateViewSet.as_view({'get': 'retrieve'}), name='aggregate_detail'),

    # Prefixes
    url(r'^prefixes/$', PrefixViewSet.as_view({'get': 'list'}), name='prefix_list'),
    url(r'^prefixes/(?P<pk>\d+)/$', PrefixViewSet.as_view({'get': 'retrieve'}), name='prefix_detail'),

    # IP addresses
    url(r'^ip-addresses/$', IPAddressViewSet.as_view({'get': 'list'}), name='ipaddress_list'),
    url(r'^ip-addresses/(?P<pk>\d+)/$', IPAddressViewSet.as_view({'get': 'retrieve'}), name='ipaddress_detail'),

    # VLAN groups
    url(r'^vlan-groups/$', VLANGroupViewSet.as_view({'get': 'list'}), name='vlangroup_list'),
    url(r'^vlan-groups/(?P<pk>\d+)/$', VLANGroupViewSet.as_view({'get': 'retrieve'}), name='vlangroup_detail'),

    # VLANs
    url(r'^vlans/$', VLANViewSet.as_view({'get': 'list'}), name='vlan_list'),
    url(r'^vlans/(?P<pk>\d+)/$', VLANViewSet.as_view({'get': 'retrieve'}), name='vlan_detail'),

    # Services
    url(r'^services/$', ServiceViewSet.as_view({'get': 'list'}), name='service_list'),
    url(r'^services/(?P<pk>\d+)/$', ServiceViewSet.as_view({'get': 'retrieve'}), name='service_detail'),

]
