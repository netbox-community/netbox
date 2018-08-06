from __future__ import unicode_literals

from django.conf.urls import url

from extras.views import ObjectChangeLogView
from . import views
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF


app_name = 'ipam'
urlpatterns = [

    # VRFs
    url(r'^vrfs/$', views.VRFListView.as_view(), name='vrf_list'),
    url(r'^vrfs/add/$', views.VRFCreateView.as_view(), name='vrf_add'),
    url(r'^vrfs/import/$', views.VRFBulkImportView.as_view(), name='vrf_import'),
    url(r'^vrfs/edit/$', views.VRFBulkEditView.as_view(), name='vrf_bulk_edit'),
    url(r'^vrfs/delete/$', views.VRFBulkDeleteView.as_view(), name='vrf_bulk_delete'),
    url(r'^vrfs/(?P<pk>\d+)/$', views.VRFView.as_view(), name='vrf'),
    url(r'^vrfs/(?P<pk>\d+)/edit/$', views.VRFEditView.as_view(), name='vrf_edit'),
    url(r'^vrfs/(?P<pk>\d+)/delete/$', views.VRFDeleteView.as_view(), name='vrf_delete'),
    url(r'^vrfs/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='vrf_changelog', kwargs={'model': VRF}),

    # RIRs
    url(r'^rirs/$', views.RIRListView.as_view(), name='rir_list'),
    url(r'^rirs/add/$', views.RIRCreateView.as_view(), name='rir_add'),
    url(r'^rirs/import/$', views.RIRBulkImportView.as_view(), name='rir_import'),
    url(r'^rirs/delete/$', views.RIRBulkDeleteView.as_view(), name='rir_bulk_delete'),
    url(r'^rirs/(?P<slug>[\w-]+)/edit/$', views.RIREditView.as_view(), name='rir_edit'),
    url(r'^vrfs/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='rir_changelog', kwargs={'model': RIR}),

    # Aggregates
    url(r'^aggregates/$', views.AggregateListView.as_view(), name='aggregate_list'),
    url(r'^aggregates/add/$', views.AggregateCreateView.as_view(), name='aggregate_add'),
    url(r'^aggregates/import/$', views.AggregateBulkImportView.as_view(), name='aggregate_import'),
    url(r'^aggregates/edit/$', views.AggregateBulkEditView.as_view(), name='aggregate_bulk_edit'),
    url(r'^aggregates/delete/$', views.AggregateBulkDeleteView.as_view(), name='aggregate_bulk_delete'),
    url(r'^aggregates/(?P<pk>\d+)/$', views.AggregateView.as_view(), name='aggregate'),
    url(r'^aggregates/(?P<pk>\d+)/edit/$', views.AggregateEditView.as_view(), name='aggregate_edit'),
    url(r'^aggregates/(?P<pk>\d+)/delete/$', views.AggregateDeleteView.as_view(), name='aggregate_delete'),
    url(r'^aggregates/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='aggregate_changelog', kwargs={'model': Aggregate}),

    # Roles
    url(r'^roles/$', views.RoleListView.as_view(), name='role_list'),
    url(r'^roles/add/$', views.RoleCreateView.as_view(), name='role_add'),
    url(r'^roles/import/$', views.RoleBulkImportView.as_view(), name='role_import'),
    url(r'^roles/delete/$', views.RoleBulkDeleteView.as_view(), name='role_bulk_delete'),
    url(r'^roles/(?P<slug>[\w-]+)/edit/$', views.RoleEditView.as_view(), name='role_edit'),
    url(r'^roles/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='role_changelog', kwargs={'model': Role}),

    # Prefixes
    url(r'^prefixes/$', views.PrefixListView.as_view(), name='prefix_list'),
    url(r'^prefixes/add/$', views.PrefixCreateView.as_view(), name='prefix_add'),
    url(r'^prefixes/import/$', views.PrefixBulkImportView.as_view(), name='prefix_import'),
    url(r'^prefixes/edit/$', views.PrefixBulkEditView.as_view(), name='prefix_bulk_edit'),
    url(r'^prefixes/delete/$', views.PrefixBulkDeleteView.as_view(), name='prefix_bulk_delete'),
    url(r'^prefixes/(?P<pk>\d+)/$', views.PrefixView.as_view(), name='prefix'),
    url(r'^prefixes/(?P<pk>\d+)/edit/$', views.PrefixEditView.as_view(), name='prefix_edit'),
    url(r'^prefixes/(?P<pk>\d+)/delete/$', views.PrefixDeleteView.as_view(), name='prefix_delete'),
    url(r'^prefixes/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='prefix_changelog', kwargs={'model': Prefix}),
    url(r'^prefixes/(?P<pk>\d+)/prefixes/$', views.PrefixPrefixesView.as_view(), name='prefix_prefixes'),
    url(r'^prefixes/(?P<pk>\d+)/ip-addresses/$', views.PrefixIPAddressesView.as_view(), name='prefix_ipaddresses'),

    # IP addresses
    url(r'^ip-addresses/$', views.IPAddressListView.as_view(), name='ipaddress_list'),
    url(r'^ip-addresses/add/$', views.IPAddressCreateView.as_view(), name='ipaddress_add'),
    url(r'^ip-addresses/bulk-add/$', views.IPAddressBulkCreateView.as_view(), name='ipaddress_bulk_add'),
    url(r'^ip-addresses/import/$', views.IPAddressBulkImportView.as_view(), name='ipaddress_import'),
    url(r'^ip-addresses/edit/$', views.IPAddressBulkEditView.as_view(), name='ipaddress_bulk_edit'),
    url(r'^ip-addresses/delete/$', views.IPAddressBulkDeleteView.as_view(), name='ipaddress_bulk_delete'),
    url(r'^ip-addresses/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='ipaddress_changelog', kwargs={'model': IPAddress}),
    url(r'^ip-addresses/assign/$', views.IPAddressAssignView.as_view(), name='ipaddress_assign'),
    url(r'^ip-addresses/(?P<pk>\d+)/$', views.IPAddressView.as_view(), name='ipaddress'),
    url(r'^ip-addresses/(?P<pk>\d+)/edit/$', views.IPAddressEditView.as_view(), name='ipaddress_edit'),
    url(r'^ip-addresses/(?P<pk>\d+)/delete/$', views.IPAddressDeleteView.as_view(), name='ipaddress_delete'),

    # VLAN groups
    url(r'^vlan-groups/$', views.VLANGroupListView.as_view(), name='vlangroup_list'),
    url(r'^vlan-groups/add/$', views.VLANGroupCreateView.as_view(), name='vlangroup_add'),
    url(r'^vlan-groups/import/$', views.VLANGroupBulkImportView.as_view(), name='vlangroup_import'),
    url(r'^vlan-groups/delete/$', views.VLANGroupBulkDeleteView.as_view(), name='vlangroup_bulk_delete'),
    url(r'^vlan-groups/(?P<pk>\d+)/edit/$', views.VLANGroupEditView.as_view(), name='vlangroup_edit'),
    url(r'^vlan-groups/(?P<pk>\d+)/vlans/$', views.VLANGroupVLANsView.as_view(), name='vlangroup_vlans'),
    url(r'^vlan-groups/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='vlangroup_changelog', kwargs={'model': VLANGroup}),

    # VLANs
    url(r'^vlans/$', views.VLANListView.as_view(), name='vlan_list'),
    url(r'^vlans/add/$', views.VLANCreateView.as_view(), name='vlan_add'),
    url(r'^vlans/import/$', views.VLANBulkImportView.as_view(), name='vlan_import'),
    url(r'^vlans/edit/$', views.VLANBulkEditView.as_view(), name='vlan_bulk_edit'),
    url(r'^vlans/delete/$', views.VLANBulkDeleteView.as_view(), name='vlan_bulk_delete'),
    url(r'^vlans/(?P<pk>\d+)/$', views.VLANView.as_view(), name='vlan'),
    url(r'^vlans/(?P<pk>\d+)/members/$', views.VLANMembersView.as_view(), name='vlan_members'),
    url(r'^vlans/(?P<pk>\d+)/edit/$', views.VLANEditView.as_view(), name='vlan_edit'),
    url(r'^vlans/(?P<pk>\d+)/delete/$', views.VLANDeleteView.as_view(), name='vlan_delete'),
    url(r'^vlans/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='vlan_changelog', kwargs={'model': VLAN}),

    # Services
    url(r'^services/$', views.ServiceListView.as_view(), name='service_list'),
    url(r'^services/edit/$', views.ServiceBulkEditView.as_view(), name='service_bulk_edit'),
    url(r'^services/delete/$', views.ServiceBulkDeleteView.as_view(), name='service_bulk_delete'),
    url(r'^services/(?P<pk>\d+)/$', views.ServiceView.as_view(), name='service'),
    url(r'^services/(?P<pk>\d+)/edit/$', views.ServiceEditView.as_view(), name='service_edit'),
    url(r'^services/(?P<pk>\d+)/delete/$', views.ServiceDeleteView.as_view(), name='service_delete'),
    url(r'^services/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='service_changelog', kwargs={'model': Service}),

]
