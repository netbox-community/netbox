from django.urls import path

from extras.views import ObjectChangeLogView, ObjectJournalView
from . import views
from .models import Aggregate, IPAddress, Prefix, RIR, Role, RouteTarget, Service, VLAN, VLANGroup, VRF

app_name = 'ipam'
urlpatterns = [

    # VRFs
    path('vrfs/', views.VRFListView.as_view(), name='vrf_list'),
    path('vrfs/add/', views.VRFEditView.as_view(), name='vrf_add'),
    path('vrfs/import/', views.VRFBulkImportView.as_view(), name='vrf_import'),
    path('vrfs/edit/', views.VRFBulkEditView.as_view(), name='vrf_bulk_edit'),
    path('vrfs/delete/', views.VRFBulkDeleteView.as_view(), name='vrf_bulk_delete'),
    path('vrfs/<int:pk>/', views.VRFView.as_view(), name='vrf'),
    path('vrfs/<int:pk>/edit/', views.VRFEditView.as_view(), name='vrf_edit'),
    path('vrfs/<int:pk>/delete/', views.VRFDeleteView.as_view(), name='vrf_delete'),
    path('vrfs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vrf_changelog', kwargs={'model': VRF}),
    path('vrfs/<int:pk>/journal/', ObjectJournalView.as_view(), name='vrf_journal', kwargs={'model': VRF}),

    # Route targets
    path('route-targets/', views.RouteTargetListView.as_view(), name='routetarget_list'),
    path('route-targets/add/', views.RouteTargetEditView.as_view(), name='routetarget_add'),
    path('route-targets/import/', views.RouteTargetBulkImportView.as_view(), name='routetarget_import'),
    path('route-targets/edit/', views.RouteTargetBulkEditView.as_view(), name='routetarget_bulk_edit'),
    path('route-targets/delete/', views.RouteTargetBulkDeleteView.as_view(), name='routetarget_bulk_delete'),
    path('route-targets/<int:pk>/', views.RouteTargetView.as_view(), name='routetarget'),
    path('route-targets/<int:pk>/edit/', views.RouteTargetEditView.as_view(), name='routetarget_edit'),
    path('route-targets/<int:pk>/delete/', views.RouteTargetDeleteView.as_view(), name='routetarget_delete'),
    path('route-targets/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='routetarget_changelog', kwargs={'model': RouteTarget}),
    path('route-targets/<int:pk>/journal/', ObjectJournalView.as_view(), name='routetarget_journal', kwargs={'model': RouteTarget}),

    # RIRs
    path('rirs/', views.RIRListView.as_view(), name='rir_list'),
    path('rirs/add/', views.RIREditView.as_view(), name='rir_add'),
    path('rirs/import/', views.RIRBulkImportView.as_view(), name='rir_import'),
    path('rirs/edit/', views.RIRBulkEditView.as_view(), name='rir_bulk_edit'),
    path('rirs/delete/', views.RIRBulkDeleteView.as_view(), name='rir_bulk_delete'),
    path('rirs/<int:pk>/edit/', views.RIREditView.as_view(), name='rir_edit'),
    path('rirs/<int:pk>/delete/', views.RIRDeleteView.as_view(), name='rir_delete'),
    path('rirs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='rir_changelog', kwargs={'model': RIR}),

    # Aggregates
    path('aggregates/', views.AggregateListView.as_view(), name='aggregate_list'),
    path('aggregates/add/', views.AggregateEditView.as_view(), name='aggregate_add'),
    path('aggregates/import/', views.AggregateBulkImportView.as_view(), name='aggregate_import'),
    path('aggregates/edit/', views.AggregateBulkEditView.as_view(), name='aggregate_bulk_edit'),
    path('aggregates/delete/', views.AggregateBulkDeleteView.as_view(), name='aggregate_bulk_delete'),
    path('aggregates/<int:pk>/', views.AggregateView.as_view(), name='aggregate'),
    path('aggregates/<int:pk>/edit/', views.AggregateEditView.as_view(), name='aggregate_edit'),
    path('aggregates/<int:pk>/delete/', views.AggregateDeleteView.as_view(), name='aggregate_delete'),
    path('aggregates/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='aggregate_changelog', kwargs={'model': Aggregate}),
    path('aggregates/<int:pk>/journal/', ObjectJournalView.as_view(), name='aggregate_journal', kwargs={'model': Aggregate}),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleEditView.as_view(), name='role_add'),
    path('roles/import/', views.RoleBulkImportView.as_view(), name='role_import'),
    path('roles/edit/', views.RoleBulkEditView.as_view(), name='role_bulk_edit'),
    path('roles/delete/', views.RoleBulkDeleteView.as_view(), name='role_bulk_delete'),
    path('roles/<int:pk>/edit/', views.RoleEditView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='role_changelog', kwargs={'model': Role}),

    # Prefixes
    path('prefixes/', views.PrefixListView.as_view(), name='prefix_list'),
    path('prefixes/add/', views.PrefixEditView.as_view(), name='prefix_add'),
    path('prefixes/import/', views.PrefixBulkImportView.as_view(), name='prefix_import'),
    path('prefixes/edit/', views.PrefixBulkEditView.as_view(), name='prefix_bulk_edit'),
    path('prefixes/delete/', views.PrefixBulkDeleteView.as_view(), name='prefix_bulk_delete'),
    path('prefixes/<int:pk>/', views.PrefixView.as_view(), name='prefix'),
    path('prefixes/<int:pk>/edit/', views.PrefixEditView.as_view(), name='prefix_edit'),
    path('prefixes/<int:pk>/delete/', views.PrefixDeleteView.as_view(), name='prefix_delete'),
    path('prefixes/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='prefix_changelog', kwargs={'model': Prefix}),
    path('prefixes/<int:pk>/journal/', ObjectJournalView.as_view(), name='prefix_journal', kwargs={'model': Prefix}),
    path('prefixes/<int:pk>/prefixes/', views.PrefixPrefixesView.as_view(), name='prefix_prefixes'),
    path('prefixes/<int:pk>/ip-addresses/', views.PrefixIPAddressesView.as_view(), name='prefix_ipaddresses'),

    # IP addresses
    path('ip-addresses/', views.IPAddressListView.as_view(), name='ipaddress_list'),
    path('ip-addresses/add/', views.IPAddressEditView.as_view(), name='ipaddress_add'),
    path('ip-addresses/bulk-add/', views.IPAddressBulkCreateView.as_view(), name='ipaddress_bulk_add'),
    path('ip-addresses/import/', views.IPAddressBulkImportView.as_view(), name='ipaddress_import'),
    path('ip-addresses/edit/', views.IPAddressBulkEditView.as_view(), name='ipaddress_bulk_edit'),
    path('ip-addresses/delete/', views.IPAddressBulkDeleteView.as_view(), name='ipaddress_bulk_delete'),
    path('ip-addresses/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='ipaddress_changelog', kwargs={'model': IPAddress}),
    path('ip-addresses/<int:pk>/journal/', ObjectJournalView.as_view(), name='ipaddress_journal', kwargs={'model': IPAddress}),
    path('ip-addresses/assign/', views.IPAddressAssignView.as_view(), name='ipaddress_assign'),
    path('ip-addresses/<int:pk>/', views.IPAddressView.as_view(), name='ipaddress'),
    path('ip-addresses/<int:pk>/edit/', views.IPAddressEditView.as_view(), name='ipaddress_edit'),
    path('ip-addresses/<int:pk>/delete/', views.IPAddressDeleteView.as_view(), name='ipaddress_delete'),

    # VLAN groups
    path('vlan-groups/', views.VLANGroupListView.as_view(), name='vlangroup_list'),
    path('vlan-groups/add/', views.VLANGroupEditView.as_view(), name='vlangroup_add'),
    path('vlan-groups/import/', views.VLANGroupBulkImportView.as_view(), name='vlangroup_import'),
    path('vlan-groups/edit/', views.VLANGroupBulkEditView.as_view(), name='vlangroup_bulk_edit'),
    path('vlan-groups/delete/', views.VLANGroupBulkDeleteView.as_view(), name='vlangroup_bulk_delete'),
    path('vlan-groups/<int:pk>/edit/', views.VLANGroupEditView.as_view(), name='vlangroup_edit'),
    path('vlan-groups/<int:pk>/delete/', views.VLANGroupDeleteView.as_view(), name='vlangroup_delete'),
    path('vlan-groups/<int:pk>/vlans/', views.VLANGroupVLANsView.as_view(), name='vlangroup_vlans'),
    path('vlan-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlangroup_changelog', kwargs={'model': VLANGroup}),

    # VLANs
    path('vlans/', views.VLANListView.as_view(), name='vlan_list'),
    path('vlans/add/', views.VLANEditView.as_view(), name='vlan_add'),
    path('vlans/import/', views.VLANBulkImportView.as_view(), name='vlan_import'),
    path('vlans/edit/', views.VLANBulkEditView.as_view(), name='vlan_bulk_edit'),
    path('vlans/delete/', views.VLANBulkDeleteView.as_view(), name='vlan_bulk_delete'),
    path('vlans/<int:pk>/', views.VLANView.as_view(), name='vlan'),
    path('vlans/<int:pk>/interfaces/', views.VLANInterfacesView.as_view(), name='vlan_interfaces'),
    path('vlans/<int:pk>/vm-interfaces/', views.VLANVMInterfacesView.as_view(), name='vlan_vminterfaces'),
    path('vlans/<int:pk>/edit/', views.VLANEditView.as_view(), name='vlan_edit'),
    path('vlans/<int:pk>/delete/', views.VLANDeleteView.as_view(), name='vlan_delete'),
    path('vlans/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlan_changelog', kwargs={'model': VLAN}),
    path('vlans/<int:pk>/journal/', ObjectJournalView.as_view(), name='vlan_journal', kwargs={'model': VLAN}),

    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/import/', views.ServiceBulkImportView.as_view(), name='service_import'),
    path('services/edit/', views.ServiceBulkEditView.as_view(), name='service_bulk_edit'),
    path('services/delete/', views.ServiceBulkDeleteView.as_view(), name='service_bulk_delete'),
    path('services/<int:pk>/', views.ServiceView.as_view(), name='service'),
    path('services/<int:pk>/edit/', views.ServiceEditView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    path('services/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='service_changelog', kwargs={'model': Service}),
    path('services/<int:pk>/journal/', ObjectJournalView.as_view(), name='service_journal', kwargs={'model': Service}),

]
