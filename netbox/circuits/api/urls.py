from __future__ import unicode_literals

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
router.register(r'_choices', views.CircuitsFieldChoicesViewSet, base_name='field-choice')

# Providers
router.register(r'providers', views.ProviderViewSet)

# Circuits
router.register(r'circuit-types', views.CircuitTypeViewSet)
router.register(r'circuits', views.CircuitViewSet)
router.register(r'circuit-terminations', views.CircuitTerminationViewSet)

app_name = 'circuits-api'
urlpatterns = router.urls
