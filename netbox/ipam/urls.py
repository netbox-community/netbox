from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'ipam'
urlpatterns = [

    # ASNs
    path('asns/', views.ASNListView.as_view(), name='asn_list'),
    path('asns/add/', views.ASNEditView.as_view(), name='asn_add'),
    path('asns/import/', views.ASNBulkImportView.as_view(), name='asn_import'),
    path('asns/edit/', views.ASNBulkEditView.as_view(), name='asn_bulk_edit'),
    path('asns/delete/', views.ASNBulkDeleteView.as_view(), name='asn_bulk_delete'),
    path('asns/<int:pk>/', include(get_model_urls('ipam', 'asn'))),

    # VRFs
    path('vrfs/', views.VRFListView.as_view(), name='vrf_list'),
    path('vrfs/add/', views.VRFEditView.as_view(), name='vrf_add'),
    path('vrfs/import/', views.VRFBulkImportView.as_view(), name='vrf_import'),
    path('vrfs/edit/', views.VRFBulkEditView.as_view(), name='vrf_bulk_edit'),
    path('vrfs/delete/', views.VRFBulkDeleteView.as_view(), name='vrf_bulk_delete'),
    path('vrfs/<int:pk>/', include(get_model_urls('ipam', 'vrf'))),

    # Route targets
    path('route-targets/', views.RouteTargetListView.as_view(), name='routetarget_list'),
    path('route-targets/add/', views.RouteTargetEditView.as_view(), name='routetarget_add'),
    path('route-targets/import/', views.RouteTargetBulkImportView.as_view(), name='routetarget_import'),
    path('route-targets/edit/', views.RouteTargetBulkEditView.as_view(), name='routetarget_bulk_edit'),
    path('route-targets/delete/', views.RouteTargetBulkDeleteView.as_view(), name='routetarget_bulk_delete'),
    path('route-targets/<int:pk>/', include(get_model_urls('ipam', 'routetarget'))),

    # RIRs
    path('rirs/', views.RIRListView.as_view(), name='rir_list'),
    path('rirs/add/', views.RIREditView.as_view(), name='rir_add'),
    path('rirs/import/', views.RIRBulkImportView.as_view(), name='rir_import'),
    path('rirs/edit/', views.RIRBulkEditView.as_view(), name='rir_bulk_edit'),
    path('rirs/delete/', views.RIRBulkDeleteView.as_view(), name='rir_bulk_delete'),
    path('rirs/<int:pk>/', include(get_model_urls('ipam', 'rir'))),

    # Aggregates
    path('aggregates/', views.AggregateListView.as_view(), name='aggregate_list'),
    path('aggregates/add/', views.AggregateEditView.as_view(), name='aggregate_add'),
    path('aggregates/import/', views.AggregateBulkImportView.as_view(), name='aggregate_import'),
    path('aggregates/edit/', views.AggregateBulkEditView.as_view(), name='aggregate_bulk_edit'),
    path('aggregates/delete/', views.AggregateBulkDeleteView.as_view(), name='aggregate_bulk_delete'),
    path('aggregates/<int:pk>/', include(get_model_urls('ipam', 'aggregate'))),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleEditView.as_view(), name='role_add'),
    path('roles/import/', views.RoleBulkImportView.as_view(), name='role_import'),
    path('roles/edit/', views.RoleBulkEditView.as_view(), name='role_bulk_edit'),
    path('roles/delete/', views.RoleBulkDeleteView.as_view(), name='role_bulk_delete'),
    path('roles/<int:pk>/', include(get_model_urls('ipam', 'role'))),

    # Prefixes
    path('prefixes/', views.PrefixListView.as_view(), name='prefix_list'),
    path('prefixes/add/', views.PrefixEditView.as_view(), name='prefix_add'),
    path('prefixes/import/', views.PrefixBulkImportView.as_view(), name='prefix_import'),
    path('prefixes/edit/', views.PrefixBulkEditView.as_view(), name='prefix_bulk_edit'),
    path('prefixes/delete/', views.PrefixBulkDeleteView.as_view(), name='prefix_bulk_delete'),
    path('prefixes/<int:pk>/', include(get_model_urls('ipam', 'prefix'))),

    # IP ranges
    path('ip-ranges/', views.IPRangeListView.as_view(), name='iprange_list'),
    path('ip-ranges/add/', views.IPRangeEditView.as_view(), name='iprange_add'),
    path('ip-ranges/import/', views.IPRangeBulkImportView.as_view(), name='iprange_import'),
    path('ip-ranges/edit/', views.IPRangeBulkEditView.as_view(), name='iprange_bulk_edit'),
    path('ip-ranges/delete/', views.IPRangeBulkDeleteView.as_view(), name='iprange_bulk_delete'),
    path('ip-ranges/<int:pk>/', include(get_model_urls('ipam', 'iprange'))),

    # IP addresses
    path('ip-addresses/', views.IPAddressListView.as_view(), name='ipaddress_list'),
    path('ip-addresses/add/', views.IPAddressEditView.as_view(), name='ipaddress_add'),
    path('ip-addresses/bulk-add/', views.IPAddressBulkCreateView.as_view(), name='ipaddress_bulk_add'),
    path('ip-addresses/import/', views.IPAddressBulkImportView.as_view(), name='ipaddress_import'),
    path('ip-addresses/edit/', views.IPAddressBulkEditView.as_view(), name='ipaddress_bulk_edit'),
    path('ip-addresses/delete/', views.IPAddressBulkDeleteView.as_view(), name='ipaddress_bulk_delete'),
    path('ip-addresses/assign/', views.IPAddressAssignView.as_view(), name='ipaddress_assign'),
    path('ip-addresses/<int:pk>/', include(get_model_urls('ipam', 'ipaddress'))),

    # FHRP groups
    path('fhrp-groups/', views.FHRPGroupListView.as_view(), name='fhrpgroup_list'),
    path('fhrp-groups/add/', views.FHRPGroupEditView.as_view(), name='fhrpgroup_add'),
    path('fhrp-groups/import/', views.FHRPGroupBulkImportView.as_view(), name='fhrpgroup_import'),
    path('fhrp-groups/edit/', views.FHRPGroupBulkEditView.as_view(), name='fhrpgroup_bulk_edit'),
    path('fhrp-groups/delete/', views.FHRPGroupBulkDeleteView.as_view(), name='fhrpgroup_bulk_delete'),
    path('fhrp-groups/<int:pk>/', include(get_model_urls('ipam', 'fhrpgroup'))),

    # FHRP group assignments
    path('fhrp-group-assignments/add/', views.FHRPGroupAssignmentEditView.as_view(), name='fhrpgroupassignment_add'),
    path('fhrp-group-assignments/<int:pk>/', include(get_model_urls('ipam', 'fhrpgroupassignment'))),

    # VLAN groups
    path('vlan-groups/', views.VLANGroupListView.as_view(), name='vlangroup_list'),
    path('vlan-groups/add/', views.VLANGroupEditView.as_view(), name='vlangroup_add'),
    path('vlan-groups/import/', views.VLANGroupBulkImportView.as_view(), name='vlangroup_import'),
    path('vlan-groups/edit/', views.VLANGroupBulkEditView.as_view(), name='vlangroup_bulk_edit'),
    path('vlan-groups/delete/', views.VLANGroupBulkDeleteView.as_view(), name='vlangroup_bulk_delete'),
    path('vlan-groups/<int:pk>/', include(get_model_urls('ipam', 'vlangroup'))),

    # VLANs
    path('vlans/', views.VLANListView.as_view(), name='vlan_list'),
    path('vlans/add/', views.VLANEditView.as_view(), name='vlan_add'),
    path('vlans/import/', views.VLANBulkImportView.as_view(), name='vlan_import'),
    path('vlans/edit/', views.VLANBulkEditView.as_view(), name='vlan_bulk_edit'),
    path('vlans/delete/', views.VLANBulkDeleteView.as_view(), name='vlan_bulk_delete'),
    path('vlans/<int:pk>/', include(get_model_urls('ipam', 'vlan'))),

    # Service templates
    path('service-templates/', views.ServiceTemplateListView.as_view(), name='servicetemplate_list'),
    path('service-templates/add/', views.ServiceTemplateEditView.as_view(), name='servicetemplate_add'),
    path('service-templates/import/', views.ServiceTemplateBulkImportView.as_view(), name='servicetemplate_import'),
    path('service-templates/edit/', views.ServiceTemplateBulkEditView.as_view(), name='servicetemplate_bulk_edit'),
    path('service-templates/delete/', views.ServiceTemplateBulkDeleteView.as_view(), name='servicetemplate_bulk_delete'),
    path('service-templates/<int:pk>/', include(get_model_urls('ipam', 'servicetemplate'))),

    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/import/', views.ServiceBulkImportView.as_view(), name='service_import'),
    path('services/edit/', views.ServiceBulkEditView.as_view(), name='service_bulk_edit'),
    path('services/delete/', views.ServiceBulkDeleteView.as_view(), name='service_bulk_delete'),
    path('services/<int:pk>/', include(get_model_urls('ipam', 'service'))),

    # L2VPN
    path('l2vpns/', views.L2VPNListView.as_view(), name='l2vpn_list'),
    path('l2vpns/add/', views.L2VPNEditView.as_view(), name='l2vpn_add'),
    path('l2vpns/import/', views.L2VPNBulkImportView.as_view(), name='l2vpn_import'),
    path('l2vpns/edit/', views.L2VPNBulkEditView.as_view(), name='l2vpn_bulk_edit'),
    path('l2vpns/delete/', views.L2VPNBulkDeleteView.as_view(), name='l2vpn_bulk_delete'),
    path('l2vpns/<int:pk>/', include(get_model_urls('ipam', 'l2vpn'))),

    # L2VPN terminations
    path('l2vpn-terminations/', views.L2VPNTerminationListView.as_view(), name='l2vpntermination_list'),
    path('l2vpn-terminations/add/', views.L2VPNTerminationEditView.as_view(), name='l2vpntermination_add'),
    path('l2vpn-terminations/import/', views.L2VPNTerminationBulkImportView.as_view(), name='l2vpntermination_import'),
    path('l2vpn-terminations/edit/', views.L2VPNTerminationBulkEditView.as_view(), name='l2vpntermination_bulk_edit'),
    path('l2vpn-terminations/delete/', views.L2VPNTerminationBulkDeleteView.as_view(), name='l2vpntermination_bulk_delete'),
    path('l2vpn-terminations/<int:pk>/', include(get_model_urls('ipam', 'l2vpntermination'))),
]
