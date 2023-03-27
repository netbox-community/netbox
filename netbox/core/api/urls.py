from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.CoreRootView

# Data sources
router.register('data-sources', views.DataSourceViewSet)
router.register('data-files', views.DataFileViewSet)

# Jobs
router.register('jobs', views.JobViewSet)

app_name = 'core-api'
urlpatterns = router.urls
