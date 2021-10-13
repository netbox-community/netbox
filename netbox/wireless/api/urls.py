from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.WirelessRootView

router.register('wireless-lans', views.WirelessLANViewSet)
router.register('wireless-links', views.WirelessLinkViewSet)

app_name = 'wireless-api'
urlpatterns = router.urls
