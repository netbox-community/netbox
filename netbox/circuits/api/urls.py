from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'providers', views.ProviderViewSet)
router.register(r'circuit-types', views.CircuitTypeViewSet)
router.register(r'circuits', views.CircuitViewSet)
router.register(r'circuit-terminations', views.CircuitTerminationViewSet)
