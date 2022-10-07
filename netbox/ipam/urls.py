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
    path('asns/<int:pk>/', views.ASNView.as_view(), name='asn'),
    path('asns/<int:pk>/edit/', views.ASNEditView.as_view(), name='asn_edit'),
    path('asns/<int:pk>/delete/', views.ASNDeleteView.as_view(), name='asn_delete'),
    path('asns/<int:pk>/', include(get_model_urls('ipam', 'asn'))),

    # VRFs
    path('vrfs/', views.VRFListView.as_view(), name='vrf_list'),
    path('vrfs/add/', views.VRFEditView.as_view(), name='vrf_add'),
    path('vrfs/import/', views.VRFBulkImportView.as_view(), name='vrf_import'),
    path('vrfs/edit/', views.VRFBulkEditView.as_view(), name='vrf_bulk_edit'),
    path('vrfs/delete/', views.VRFBulkDeleteView.as_view(), name='vrf_bulk_delete'),
    path('vrfs/<int:pk>/', views.VRFView.as_view(), name='vrf'),
    path('vrfs/<int:pk>/edit/', views.VRFEditView.as_view(), name='vrf_edit'),
    path('vrfs/<int:pk>/delete/', views.VRFDeleteView.as_view(), name='vrf_delete'),
    path('vrfs/<int:pk>/', include(get_model_urls('ipam', 'vrf'))),

    # Route targets
    path('route-targets/', views.RouteTargetListView.as_view(), name='routetarget_list'),
    path('route-targets/add/', views.RouteTargetEditView.as_view(), name='routetarget_add'),
    path('route-targets/import/', views.RouteTargetBulkImportView.as_view(), name='routetarget_import'),
    path('route-targets/edit/', views.RouteTargetBulkEditView.as_view(), name='routetarget_bulk_edit'),
    path('route-targets/delete/', views.RouteTargetBulkDeleteView.as_view(), name='routetarget_bulk_delete'),
    path('route-targets/<int:pk>/', views.RouteTargetView.as_view(), name='routetarget'),
    path('route-targets/<int:pk>/edit/', views.RouteTargetEditView.as_view(), name='routetarget_edit'),
    path('route-targets/<int:pk>/delete/', views.RouteTargetDeleteView.as_view(), name='routetarget_delete'),
    path('route-targets/<int:pk>/', include(get_model_urls('ipam', 'routetarget'))),

    # RIRs
    path('rirs/', views.RIRListView.as_view(), name='rir_list'),
    path('rirs/add/', views.RIREditView.as_view(), name='rir_add'),
    path('rirs/import/', views.RIRBulkImportView.as_view(), name='rir_import'),
    path('rirs/edit/', views.RIRBulkEditView.as_view(), name='rir_bulk_edit'),
    path('rirs/delete/', views.RIRBulkDeleteView.as_view(), name='rir_bulk_delete'),
    path('rirs/<int:pk>/', views.RIRView.as_view(), name='rir'),
    path('rirs/<int:pk>/edit/', views.RIREditView.as_view(), name='rir_edit'),
    path('rirs/<int:pk>/delete/', views.RIRDeleteView.as_view(), name='rir_delete'),
    path('rirs/<int:pk>/', include(get_model_urls('ipam', 'rir'))),

    # Aggregates
    path('aggregates/', views.AggregateListView.as_view(), name='aggregate_list'),
    path('aggregates/add/', views.AggregateEditView.as_view(), name='aggregate_add'),
    path('aggregates/import/', views.AggregateBulkImportView.as_view(), name='aggregate_import'),
    path('aggregates/edit/', views.AggregateBulkEditView.as_view(), name='aggregate_bulk_edit'),
    path('aggregates/delete/', views.AggregateBulkDeleteView.as_view(), name='aggregate_bulk_delete'),
    path('aggregates/<int:pk>/', views.AggregateView.as_view(), name='aggregate'),
    path('aggregates/<int:pk>/edit/', views.AggregateEditView.as_view(), name='aggregate_edit'),
    path('aggregates/<int:pk>/delete/', views.AggregateDeleteView.as_view(), name='aggregate_delete'),
    path('aggregates/<int:pk>/', include(get_model_urls('ipam', 'aggregate'))),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleEditView.as_view(), name='role_add'),
    path('roles/import/', views.RoleBulkImportView.as_view(), name='role_import'),
    path('roles/edit/', views.RoleBulkEditView.as_view(), name='role_bulk_edit'),
    path('roles/delete/', views.RoleBulkDeleteView.as_view(), name='role_bulk_delete'),
    path('roles/<int:pk>/', views.RoleView.as_view(), name='role'),
    path('roles/<int:pk>/edit/', views.RoleEditView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/<int:pk>/', include(get_model_urls('ipam', 'role'))),

    # Prefixes
    path('prefixes/', views.PrefixListView.as_view(), name='prefix_list'),
    path('prefixes/add/', views.PrefixEditView.as_view(), name='prefix_add'),
    path('prefixes/import/', views.PrefixBulkImportView.as_view(), name='prefix_import'),
    path('prefixes/edit/', views.PrefixBulkEditView.as_view(), name='prefix_bulk_edit'),
    path('prefixes/delete/', views.PrefixBulkDeleteView.as_view(), name='prefix_bulk_delete'),
    path('prefixes/<int:pk>/', views.PrefixView.as_view(), name='prefix'),
    path('prefixes/<int:pk>/edit/', views.PrefixEditView.as_view(), name='prefix_edit'),
    path('prefixes/<int:pk>/delete/', views.PrefixDeleteView.as_view(), name='prefix_delete'),
    path('prefixes/<int:pk>/', include(get_model_urls('ipam', 'prefix'))),

    # IP ranges
    path('ip-ranges/', views.IPRangeListView.as_view(), name='iprange_list'),
    path('ip-ranges/add/', views.IPRangeEditView.as_view(), name='iprange_add'),
    path('ip-ranges/import/', views.IPRangeBulkImportView.as_view(), name='iprange_import'),
    path('ip-ranges/edit/', views.IPRangeBulkEditView.as_view(), name='iprange_bulk_edit'),
    path('ip-ranges/delete/', views.IPRangeBulkDeleteView.as_view(), name='iprange_bulk_delete'),
    path('ip-ranges/<int:pk>/', views.IPRangeView.as_view(), name='iprange'),
    path('ip-ranges/<int:pk>/edit/', views.IPRangeEditView.as_view(), name='iprange_edit'),
    path('ip-ranges/<int:pk>/delete/', views.IPRangeDeleteView.as_view(), name='iprange_delete'),
    path('ip-ranges/<int:pk>/', include(get_model_urls('ipam', 'iprange'))),

    # IP addresses
    path('ip-addresses/', views.IPAddressListView.as_view(), name='ipaddress_list'),
    path('ip-addresses/add/', views.IPAddressEditView.as_view(), name='ipaddress_add'),
    path('ip-addresses/bulk-add/', views.IPAddressBulkCreateView.as_view(), name='ipaddress_bulk_add'),
    path('ip-addresses/import/', views.IPAddressBulkImportView.as_view(), name='ipaddress_import'),
    path('ip-addresses/edit/', views.IPAddressBulkEditView.as_view(), name='ipaddress_bulk_edit'),
    path('ip-addresses/delete/', views.IPAddressBulkDeleteView.as_view(), name='ipaddress_bulk_delete'),
    path('ip-addresses/assign/', views.IPAddressAssignView.as_view(), name='ipaddress_assign'),
    path('ip-addresses/<int:pk>/', views.IPAddressView.as_view(), name='ipaddress'),
    path('ip-addresses/<int:pk>/edit/', views.IPAddressEditView.as_view(), name='ipaddress_edit'),
    path('ip-addresses/<int:pk>/delete/', views.IPAddressDeleteView.as_view(), name='ipaddress_delete'),
    path('ip-addresses/<int:pk>/', include(get_model_urls('ipam', 'ipaddress'))),

    # FHRP groups
    path('fhrp-groups/', views.FHRPGroupListView.as_view(), name='fhrpgroup_list'),
    path('fhrp-groups/add/', views.FHRPGroupEditView.as_view(), name='fhrpgroup_add'),
    path('fhrp-groups/import/', views.FHRPGroupBulkImportView.as_view(), name='fhrpgroup_import'),
    path('fhrp-groups/edit/', views.FHRPGroupBulkEditView.as_view(), name='fhrpgroup_bulk_edit'),
    path('fhrp-groups/delete/', views.FHRPGroupBulkDeleteView.as_view(), name='fhrpgroup_bulk_delete'),
    path('fhrp-groups/<int:pk>/', views.FHRPGroupView.as_view(), name='fhrpgroup'),
    path('fhrp-groups/<int:pk>/edit/', views.FHRPGroupEditView.as_view(), name='fhrpgroup_edit'),
    path('fhrp-groups/<int:pk>/delete/', views.FHRPGroupDeleteView.as_view(), name='fhrpgroup_delete'),
    path('fhrp-groups/<int:pk>/', include(get_model_urls('ipam', 'fhrpgroup'))),

    # FHRP group assignments
    path('fhrp-group-assignments/add/', views.FHRPGroupAssignmentEditView.as_view(), name='fhrpgroupassignment_add'),
    path('fhrp-group-assignments/<int:pk>/edit/', views.FHRPGroupAssignmentEditView.as_view(), name='fhrpgroupassignment_edit'),
    path('fhrp-group-assignments/<int:pk>/delete/', views.FHRPGroupAssignmentDeleteView.as_view(), name='fhrpgroupassignment_delete'),

    # VLAN groups
    path('vlan-groups/', views.VLANGroupListView.as_view(), name='vlangroup_list'),
    path('vlan-groups/add/', views.VLANGroupEditView.as_view(), name='vlangroup_add'),
    path('vlan-groups/import/', views.VLANGroupBulkImportView.as_view(), name='vlangroup_import'),
    path('vlan-groups/edit/', views.VLANGroupBulkEditView.as_view(), name='vlangroup_bulk_edit'),
    path('vlan-groups/delete/', views.VLANGroupBulkDeleteView.as_view(), name='vlangroup_bulk_delete'),
    path('vlan-groups/<int:pk>/', views.VLANGroupView.as_view(), name='vlangroup'),
    path('vlan-groups/<int:pk>/edit/', views.VLANGroupEditView.as_view(), name='vlangroup_edit'),
    path('vlan-groups/<int:pk>/delete/', views.VLANGroupDeleteView.as_view(), name='vlangroup_delete'),
    path('vlan-groups/<int:pk>/', include(get_model_urls('ipam', 'vlangroup'))),

    # VLANs
    path('vlans/', views.VLANListView.as_view(), name='vlan_list'),
    path('vlans/add/', views.VLANEditView.as_view(), name='vlan_add'),
    path('vlans/import/', views.VLANBulkImportView.as_view(), name='vlan_import'),
    path('vlans/edit/', views.VLANBulkEditView.as_view(), name='vlan_bulk_edit'),
    path('vlans/delete/', views.VLANBulkDeleteView.as_view(), name='vlan_bulk_delete'),
    path('vlans/<int:pk>/', views.VLANView.as_view(), name='vlan'),
    path('vlans/<int:pk>/edit/', views.VLANEditView.as_view(), name='vlan_edit'),
    path('vlans/<int:pk>/delete/', views.VLANDeleteView.as_view(), name='vlan_delete'),
    path('vlans/<int:pk>/', include(get_model_urls('ipam', 'vlan'))),

    # Service templates
    path('service-templates/', views.ServiceTemplateListView.as_view(), name='servicetemplate_list'),
    path('service-templates/add/', views.ServiceTemplateEditView.as_view(), name='servicetemplate_add'),
    path('service-templates/import/', views.ServiceTemplateBulkImportView.as_view(), name='servicetemplate_import'),
    path('service-templates/edit/', views.ServiceTemplateBulkEditView.as_view(), name='servicetemplate_bulk_edit'),
    path('service-templates/delete/', views.ServiceTemplateBulkDeleteView.as_view(), name='servicetemplate_bulk_delete'),
    path('service-templates/<int:pk>/', views.ServiceTemplateView.as_view(), name='servicetemplate'),
    path('service-templates/<int:pk>/edit/', views.ServiceTemplateEditView.as_view(), name='servicetemplate_edit'),
    path('service-templates/<int:pk>/delete/', views.ServiceTemplateDeleteView.as_view(), name='servicetemplate_delete'),
    path('service-templates/<int:pk>/', include(get_model_urls('ipam', 'servicetemplate'))),

    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/import/', views.ServiceBulkImportView.as_view(), name='service_import'),
    path('services/edit/', views.ServiceBulkEditView.as_view(), name='service_bulk_edit'),
    path('services/delete/', views.ServiceBulkDeleteView.as_view(), name='service_bulk_delete'),
    path('services/<int:pk>/', views.ServiceView.as_view(), name='service'),
    path('services/<int:pk>/edit/', views.ServiceEditView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    path('services/<int:pk>/', include(get_model_urls('ipam', 'service'))),

    # L2VPN
    path('l2vpns/', views.L2VPNListView.as_view(), name='l2vpn_list'),
    path('l2vpns/add/', views.L2VPNEditView.as_view(), name='l2vpn_add'),
    path('l2vpns/import/', views.L2VPNBulkImportView.as_view(), name='l2vpn_import'),
    path('l2vpns/edit/', views.L2VPNBulkEditView.as_view(), name='l2vpn_bulk_edit'),
    path('l2vpns/delete/', views.L2VPNBulkDeleteView.as_view(), name='l2vpn_bulk_delete'),
    path('l2vpns/<int:pk>/', views.L2VPNView.as_view(), name='l2vpn'),
    path('l2vpns/<int:pk>/edit/', views.L2VPNEditView.as_view(), name='l2vpn_edit'),
    path('l2vpns/<int:pk>/delete/', views.L2VPNDeleteView.as_view(), name='l2vpn_delete'),
    path('l2vpns/<int:pk>/', include(get_model_urls('ipam', 'l2vpn'))),

    # L2VPN terminations
    path('l2vpn-terminations/', views.L2VPNTerminationListView.as_view(), name='l2vpntermination_list'),
    path('l2vpn-terminations/add/', views.L2VPNTerminationEditView.as_view(), name='l2vpntermination_add'),
    path('l2vpn-terminations/import/', views.L2VPNTerminationBulkImportView.as_view(), name='l2vpntermination_import'),
    path('l2vpn-terminations/edit/', views.L2VPNTerminationBulkEditView.as_view(), name='l2vpntermination_bulk_edit'),
    path('l2vpn-terminations/delete/', views.L2VPNTerminationBulkDeleteView.as_view(), name='l2vpntermination_bulk_delete'),
    path('l2vpn-terminations/<int:pk>/', views.L2VPNTerminationView.as_view(), name='l2vpntermination'),
    path('l2vpn-terminations/<int:pk>/edit/', views.L2VPNTerminationEditView.as_view(), name='l2vpntermination_edit'),
    path('l2vpn-terminations/<int:pk>/delete/', views.L2VPNTerminationDeleteView.as_view(), name='l2vpntermination_delete'),
    path('l2vpn-terminations/<int:pk>/', include(get_model_urls('ipam', 'l2vpntermination'))),
]
