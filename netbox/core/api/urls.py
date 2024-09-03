from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.CoreRootView

router.register('data-sources', views.DataSourceViewSet)
router.register('data-files', views.DataFileViewSet)
router.register('jobs', views.JobViewSet)
router.register('object-changes', views.ObjectChangeViewSet)

app_name = 'core-api'
urlpatterns = router.urls
