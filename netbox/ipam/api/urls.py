from django.conf.urls import include, url

from rest_framework import routers

from .views import (
    AggregateViewSet, IPAddressViewSet, PrefixViewSet, RIRViewSet, RoleViewSet, ServiceViewSet, VLANViewSet,
    VLANGroupViewSet, VRFViewSet,
)


router = routers.DefaultRouter()
router.register(r'vrfs', VRFViewSet)
router.register(r'rirs', RIRViewSet)
router.register(r'aggregates', AggregateViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'prefixes', PrefixViewSet)
router.register(r'ip-addresses', IPAddressViewSet)
router.register(r'vlan-groups', VLANGroupViewSet)
router.register(r'vlans', VLANViewSet)
router.register(r'services', ServiceViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

]
