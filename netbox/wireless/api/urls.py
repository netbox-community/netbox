from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.WirelessRootView

# SSIDs
router.register('ssids', views.SSIDViewSet)

app_name = 'wireless-api'
urlpatterns = router.urls
