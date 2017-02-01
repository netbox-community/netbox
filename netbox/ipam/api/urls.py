from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'vrfs', views.VRFViewSet)
router.register(r'rirs', views.RIRViewSet)
router.register(r'aggregates', views.AggregateViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'prefixes', views.PrefixViewSet)
router.register(r'ip-addresses', views.IPAddressViewSet)
router.register(r'vlan-groups', views.VLANGroupViewSet)
router.register(r'vlans', views.VLANViewSet)
router.register(r'services', views.ServiceViewSet)
