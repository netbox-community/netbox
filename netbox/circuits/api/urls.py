from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.CircuitsRootView

# Providers
router.register('providers', views.ProviderViewSet)

# Circuits
router.register('circuit-types', views.CircuitTypeViewSet)
router.register('circuits', views.CircuitViewSet)
router.register('circuit-terminations', views.CircuitTerminationViewSet)

# Provider networks
router.register('provider-networks', views.ProviderNetworkViewSet)

app_name = 'circuits-api'
urlpatterns = router.urls
