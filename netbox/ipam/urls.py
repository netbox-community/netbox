from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF

app_name = 'ipam'
urlpatterns = [

    # VRFs
    path(r'vrfs/', views.VRFListView.as_view(), name='vrf_list'),
    path(r'vrfs/add/', views.VRFCreateView.as_view(), name='vrf_add'),
    path(r'vrfs/import/', views.VRFBulkImportView.as_view(), name='vrf_import'),
    path(r'vrfs/edit/', views.VRFBulkEditView.as_view(), name='vrf_bulk_edit'),
    path(r'vrfs/delete/', views.VRFBulkDeleteView.as_view(), name='vrf_bulk_delete'),
    path(r'vrfs/<int:pk>/', views.VRFView.as_view(), name='vrf'),
    path(r'vrfs/<int:pk>/edit/', views.VRFEditView.as_view(), name='vrf_edit'),
    path(r'vrfs/<int:pk>/delete/', views.VRFDeleteView.as_view(), name='vrf_delete'),
    path(r'vrfs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vrf_changelog', kwargs={'model': VRF}),

    # RIRs
    path(r'rirs/', views.RIRListView.as_view(), name='rir_list'),
    path(r'rirs/add/', views.RIRCreateView.as_view(), name='rir_add'),
    path(r'rirs/import/', views.RIRBulkImportView.as_view(), name='rir_import'),
    path(r'rirs/delete/', views.RIRBulkDeleteView.as_view(), name='rir_bulk_delete'),
    path(r'rirs/<slug:slug>/edit/', views.RIREditView.as_view(), name='rir_edit'),
    path(r'vrfs/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='rir_changelog', kwargs={'model': RIR}),

    # Aggregates
    path(r'aggregates/', views.AggregateListView.as_view(), name='aggregate_list'),
    path(r'aggregates/add/', views.AggregateCreateView.as_view(), name='aggregate_add'),
    path(r'aggregates/import/', views.AggregateBulkImportView.as_view(), name='aggregate_import'),
    path(r'aggregates/edit/', views.AggregateBulkEditView.as_view(), name='aggregate_bulk_edit'),
    path(r'aggregates/delete/', views.AggregateBulkDeleteView.as_view(), name='aggregate_bulk_delete'),
    path(r'aggregates/<int:pk>/', views.AggregateView.as_view(), name='aggregate'),
    path(r'aggregates/<int:pk>/edit/', views.AggregateEditView.as_view(), name='aggregate_edit'),
    path(r'aggregates/<int:pk>/delete/', views.AggregateDeleteView.as_view(), name='aggregate_delete'),
    path(r'aggregates/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='aggregate_changelog', kwargs={'model': Aggregate}),

    # Roles
    path(r'roles/', views.RoleListView.as_view(), name='role_list'),
    path(r'roles/add/', views.RoleCreateView.as_view(), name='role_add'),
    path(r'roles/import/', views.RoleBulkImportView.as_view(), name='role_import'),
    path(r'roles/delete/', views.RoleBulkDeleteView.as_view(), name='role_bulk_delete'),
    path(r'roles/<slug:slug>/edit/', views.RoleEditView.as_view(), name='role_edit'),
    path(r'roles/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='role_changelog', kwargs={'model': Role}),

    # Prefixes
    path(r'prefixes/', views.PrefixListView.as_view(), name='prefix_list'),
    path(r'prefixes/add/', views.PrefixCreateView.as_view(), name='prefix_add'),
    path(r'prefixes/import/', views.PrefixBulkImportView.as_view(), name='prefix_import'),
    path(r'prefixes/edit/', views.PrefixBulkEditView.as_view(), name='prefix_bulk_edit'),
    path(r'prefixes/delete/', views.PrefixBulkDeleteView.as_view(), name='prefix_bulk_delete'),
    path(r'prefixes/<int:pk>/', views.PrefixView.as_view(), name='prefix'),
    path(r'prefixes/<int:pk>/edit/', views.PrefixEditView.as_view(), name='prefix_edit'),
    path(r'prefixes/<int:pk>/delete/', views.PrefixDeleteView.as_view(), name='prefix_delete'),
    path(r'prefixes/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='prefix_changelog', kwargs={'model': Prefix}),
    path(r'prefixes/<int:pk>/prefixes/', views.PrefixPrefixesView.as_view(), name='prefix_prefixes'),
    path(r'prefixes/<int:pk>/ip-addresses/', views.PrefixIPAddressesView.as_view(), name='prefix_ipaddresses'),

    # IP addresses
    path(r'ip-addresses/', views.IPAddressListView.as_view(), name='ipaddress_list'),
    path(r'ip-addresses/add/', views.IPAddressCreateView.as_view(), name='ipaddress_add'),
    path(r'ip-addresses/bulk-add/', views.IPAddressBulkCreateView.as_view(), name='ipaddress_bulk_add'),
    path(r'ip-addresses/import/', views.IPAddressBulkImportView.as_view(), name='ipaddress_import'),
    path(r'ip-addresses/edit/', views.IPAddressBulkEditView.as_view(), name='ipaddress_bulk_edit'),
    path(r'ip-addresses/delete/', views.IPAddressBulkDeleteView.as_view(), name='ipaddress_bulk_delete'),
    path(r'ip-addresses/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='ipaddress_changelog', kwargs={'model': IPAddress}),
    path(r'ip-addresses/assign/', views.IPAddressAssignView.as_view(), name='ipaddress_assign'),
    path(r'ip-addresses/<int:pk>/', views.IPAddressView.as_view(), name='ipaddress'),
    path(r'ip-addresses/<int:pk>/edit/', views.IPAddressEditView.as_view(), name='ipaddress_edit'),
    path(r'ip-addresses/<int:pk>/delete/', views.IPAddressDeleteView.as_view(), name='ipaddress_delete'),

    # VLAN groups
    path(r'vlan-groups/', views.VLANGroupListView.as_view(), name='vlangroup_list'),
    path(r'vlan-groups/add/', views.VLANGroupCreateView.as_view(), name='vlangroup_add'),
    path(r'vlan-groups/import/', views.VLANGroupBulkImportView.as_view(), name='vlangroup_import'),
    path(r'vlan-groups/delete/', views.VLANGroupBulkDeleteView.as_view(), name='vlangroup_bulk_delete'),
    path(r'vlan-groups/<int:pk>/edit/', views.VLANGroupEditView.as_view(), name='vlangroup_edit'),
    path(r'vlan-groups/<int:pk>/vlans/', views.VLANGroupVLANsView.as_view(), name='vlangroup_vlans'),
    path(r'vlan-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlangroup_changelog', kwargs={'model': VLANGroup}),

    # VLANs
    path(r'vlans/', views.VLANListView.as_view(), name='vlan_list'),
    path(r'vlans/add/', views.VLANCreateView.as_view(), name='vlan_add'),
    path(r'vlans/import/', views.VLANBulkImportView.as_view(), name='vlan_import'),
    path(r'vlans/edit/', views.VLANBulkEditView.as_view(), name='vlan_bulk_edit'),
    path(r'vlans/delete/', views.VLANBulkDeleteView.as_view(), name='vlan_bulk_delete'),
    path(r'vlans/<int:pk>/', views.VLANView.as_view(), name='vlan'),
    path(r'vlans/<int:pk>/members/', views.VLANMembersView.as_view(), name='vlan_members'),
    path(r'vlans/<int:pk>/edit/', views.VLANEditView.as_view(), name='vlan_edit'),
    path(r'vlans/<int:pk>/delete/', views.VLANDeleteView.as_view(), name='vlan_delete'),
    path(r'vlans/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlan_changelog', kwargs={'model': VLAN}),

    # Services
    path(r'services/', views.ServiceListView.as_view(), name='service_list'),
    path(r'services/edit/', views.ServiceBulkEditView.as_view(), name='service_bulk_edit'),
    path(r'services/delete/', views.ServiceBulkDeleteView.as_view(), name='service_bulk_delete'),
    path(r'services/<int:pk>/', views.ServiceView.as_view(), name='service'),
    path(r'services/<int:pk>/edit/', views.ServiceEditView.as_view(), name='service_edit'),
    path(r'services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    path(r'services/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='service_changelog', kwargs={'model': Service}),

]
