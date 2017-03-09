from rest_framework import routers

from . import views


router = routers.DefaultRouter()

# Topology maps
router.register(r'topology-maps', views.TopologyMapViewSet)

urlpatterns = router.urls
