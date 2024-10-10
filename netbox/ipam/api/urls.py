from django.urls import path

from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.IPAMRootView

router.register('asns', views.ASNViewSet)
router.register('asn-ranges', views.ASNRangeViewSet)
router.register('vrfs', views.VRFViewSet)
router.register('route-targets', views.RouteTargetViewSet)
router.register('rirs', views.RIRViewSet)
router.register('aggregates', views.AggregateViewSet)
router.register('roles', views.RoleViewSet)
router.register('prefixes', views.PrefixViewSet)
router.register('ip-ranges', views.IPRangeViewSet)
router.register('ip-addresses', views.IPAddressViewSet)
router.register('fhrp-groups', views.FHRPGroupViewSet)
router.register('fhrp-group-assignments', views.FHRPGroupAssignmentViewSet)
router.register('vlan-groups', views.VLANGroupViewSet)
router.register('vlans', views.VLANViewSet)
router.register('vlan-translation-policies', views.VLANTranslationPolicyViewSet)
router.register('vlan-translation-rules', views.VLANTranslationRuleViewSet)
router.register('service-templates', views.ServiceTemplateViewSet)
router.register('services', views.ServiceViewSet)

app_name = 'ipam-api'

urlpatterns = [
    path(
        'asn-ranges/<int:pk>/available-asns/',
        views.AvailableASNsView.as_view(),
        name='asnrange-available-asns'
    ),
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
