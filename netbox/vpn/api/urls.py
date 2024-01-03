from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.APIRootView = views.VPNRootView
router.register('ike-policies', views.IKEPolicyViewSet)
router.register('ike-proposals', views.IKEProposalViewSet)
router.register('ipsec-policies', views.IPSecPolicyViewSet)
router.register('ipsec-proposals', views.IPSecProposalViewSet)
router.register('ipsec-profiles', views.IPSecProfileViewSet)
router.register('tunnel-groups', views.TunnelGroupViewSet)
router.register('tunnels', views.TunnelViewSet)
router.register('tunnel-terminations', views.TunnelTerminationViewSet)
router.register('l2vpns', views.L2VPNViewSet)
router.register('l2vpn-terminations', views.L2VPNTerminationViewSet)

app_name = 'vpn-api'
urlpatterns = router.urls
