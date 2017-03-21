from rest_framework import routers

from . import views


class CircuitsRootView(routers.APIRootView):
    """
    Circuits API root view
    """
    def get_view_name(self):
        return 'Circuits'


router = routers.DefaultRouter()
router.APIRootView = CircuitsRootView

# Providers
router.register(r'providers', views.ProviderViewSet)

# Circuits
router.register(r'circuit-types', views.CircuitTypeViewSet)
router.register(r'circuits', views.CircuitViewSet)
router.register(r'circuit-terminations', views.CircuitTerminationViewSet)

urlpatterns = router.urls
