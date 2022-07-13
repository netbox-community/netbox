from django.urls import path

from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.IPAMRootView

# ASNs
router.register('asns', views.ASNViewSet)

# VRFs
router.register('vrfs', views.VRFViewSet)

# Route targets
router.register('route-targets', views.RouteTargetViewSet)

# RIRs
router.register('rirs', views.RIRViewSet)

# Aggregates
router.register('aggregates', views.AggregateViewSet)

# Prefixes
router.register('roles', views.RoleViewSet)
router.register('prefixes', views.PrefixViewSet)

# IP ranges
router.register('ip-ranges', views.IPRangeViewSet)

# IP addresses
router.register('ip-addresses', views.IPAddressViewSet)

# FHRP groups
router.register('fhrp-groups', views.FHRPGroupViewSet)
router.register('fhrp-group-assignments', views.FHRPGroupAssignmentViewSet)

# VLANs
router.register('vlan-groups', views.VLANGroupViewSet)
router.register('vlans', views.VLANViewSet)

# Services
router.register('service-templates', views.ServiceTemplateViewSet)
router.register('services', views.ServiceViewSet)

# L2VPN
router.register('l2vpns', views.L2VPNViewSet)
router.register('l2vpn-terminations', views.L2VPNTerminationViewSet)

app_name = 'ipam-api'

urlpatterns = [
    path(
        'ip-ranges/<int:pk>/available-ips/',
        views.IPRangeAvailableIPAddressesView.as_view(),
        name='iprange-available-ips'
    ),
    path(
        'prefixes/<int:pk>/available-prefixes/',
        views.AvailablePrefixesView.as_view(),
        name='prefix-available-prefixes'
    ),
    path(
        'prefixes/<int:pk>/available-ips/',
        views.PrefixAvailableIPAddressesView.as_view(),
        name='prefix-available-ips'
    ),
    path(
        'vlan-groups/<int:pk>/available-vlans/',
        views.AvailableVLANsView.as_view(),
        name='vlangroup-available-vlans'
    ),
]

urlpatterns += router.urls
