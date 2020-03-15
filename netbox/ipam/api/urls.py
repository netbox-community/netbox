from rest_framework import routers

from . import views


class IPAMRootView(routers.APIRootView):
    """
    IPAM API root view
    """
    def get_view_name(self):
        return 'IPAM'


router = routers.DefaultRouter()
router.APIRootView = IPAMRootView

# VRFs
router.register('vrfs', views.VRFViewSet)

# RIRs
router.register('rirs', views.RIRViewSet)

# Aggregates
router.register('aggregates', views.AggregateViewSet)

# Prefixes
router.register('roles', views.RoleViewSet)
router.register('prefixes', views.PrefixViewSet)

# IP addresses
router.register('ip-addresses', views.IPAddressViewSet)

# VLANs
router.register('vlan-groups', views.VLANGroupViewSet)
router.register('vlans', views.VLANViewSet)

# Services
router.register('services', views.ServiceViewSet)

app_name = 'ipam-api'
urlpatterns = router.urls
