from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.CircuitsRootView

# Providers
router.register('providers', views.ProviderViewSet)
router.register('provider-accounts', views.ProviderAccountViewSet)
router.register('provider-networks', views.ProviderNetworkViewSet)

# Circuits
router.register('circuit-types', views.CircuitTypeViewSet)
router.register('circuits', views.CircuitViewSet)
router.register('circuit-terminations', views.CircuitTerminationViewSet)
router.register('circuit-groups', views.CircuitGroupViewSet)
router.register('circuit-group-assignments', views.CircuitGroupAssignmentViewSet)

# Virtual circuits
router.register('virtual-circuits', views.VirtualCircuitViewSet)
router.register('virtual-circuit-terminations', views.VirtualCircuitTerminationViewSet)

app_name = 'circuits-api'
urlpatterns = router.urls
