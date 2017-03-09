from rest_framework import routers

from . import views


router = routers.DefaultRouter()

# Topology maps
router.register(r'topology-maps', views.TopologyMapViewSet)

# Recent activity
router.register(r'recent-activity', views.RecentActivityViewSet)

urlpatterns = router.urls
