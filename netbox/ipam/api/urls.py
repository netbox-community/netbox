from __future__ import unicode_literals

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

# Field choices
router.register(r'_choices', views.IPAMFieldChoicesViewSet, base_name='field-choice')

# VRFs
router.register(r'vrfs', views.VRFViewSet)

# RIRs
router.register(r'rirs', views.RIRViewSet)

# Aggregates
router.register(r'aggregates', views.AggregateViewSet)

# Prefixes
router.register(r'roles', views.RoleViewSet)
router.register(r'prefixes', views.PrefixViewSet)

# IP addresses
router.register(r'ip-addresses', views.IPAddressViewSet)

# VLANs
router.register(r'vlan-groups', views.VLANGroupViewSet)
router.register(r'vlans', views.VLANViewSet)

# Services
router.register(r'services', views.ServiceViewSet)

app_name = 'ipam-api'
urlpatterns = router.urls
