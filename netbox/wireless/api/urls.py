from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.WirelessRootView

router.register('wireless-lan-groups', views.WirelessLANGroupViewSet)
router.register('wireless-lans', views.WirelessLANViewSet)
router.register('wireless-links', views.WirelessLinkViewSet)

app_name = 'wireless-api'
urlpatterns = router.urls
