from rest_framework import routers
from .views import DummyViewSet

router = routers.DefaultRouter()
router.register('dummy-models', DummyViewSet)
urlpatterns = router.urls
