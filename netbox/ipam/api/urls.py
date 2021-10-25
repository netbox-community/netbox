from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
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

# VLANs
router.register('vlan-groups', views.VLANGroupViewSet)
router.register('vlans', views.VLANViewSet)

# Services
router.register('services', views.ServiceViewSet)

app_name = 'ipam-api'
urlpatterns = router.urls
