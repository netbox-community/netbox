from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.APIRootView = views.VPNRootView
router.register('ipsec-profiles', views.IPSecProfileViewSet)
router.register('tunnels', views.TunnelViewSet)
router.register('tunnel-terminations', views.TunnelTerminationViewSet)

app_name = 'vpn-api'
urlpatterns = router.urls
