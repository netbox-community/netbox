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

# Field choices
router.register('_choices', views.CircuitsFieldChoicesViewSet, basename='field-choice')

# Providers
router.register('providers', views.ProviderViewSet)

# Circuits
router.register('circuit-types', views.CircuitTypeViewSet)
router.register('circuits', views.CircuitViewSet)
router.register('circuit-terminations', views.CircuitTerminationViewSet)

app_name = 'circuits-api'
urlpatterns = router.urls
