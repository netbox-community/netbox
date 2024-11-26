from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'core-api'

router = NetBoxRouter()
router.APIRootView = views.CoreRootView

router.register('data-sources', views.DataSourceViewSet)
router.register('data-files', views.DataFileViewSet)
router.register('jobs', views.JobViewSet)
router.register('object-changes', views.ObjectChangeViewSet)
router.register('background-queues', views.BackgroundQueueViewSet, basename='rqqueue')
router.register('background-workers', views.BackgroundWorkerViewSet, basename='rqworker')
router.register('background-tasks', views.BackgroundTaskViewSet, basename='rqtask')

urlpatterns = router.urls
