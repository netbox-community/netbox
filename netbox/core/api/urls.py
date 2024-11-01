from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.CoreRootView

router.register('data-sources', views.DataSourceViewSet)
router.register('data-files', views.DataFileViewSet)
router.register('jobs', views.JobViewSet)
router.register('object-changes', views.ObjectChangeViewSet)
router.register('background-queues', views.BackgroundQueueViewSet, basename='BackgroundQueues')
router.register('background-tasks/(?P<queue_name>[\w-]+)', views.BackgroundTaskViewSet, basename='BackgroundTasks')
router.register('background-tasks/(?P<queue_name>[\w-]+)/deferred', views.BackgroundTaskDeferredViewSet, basename='BackgroundTaskDeferred')
router.register('background-tasks/(?P<queue_name>[\w-]+)/failed', views.BackgroundTaskFailedViewSet, basename='BackgroundTaskFailed')
router.register('background-tasks/(?P<queue_name>[\w-]+)/finished', views.BackgroundTaskFinishedViewSet, basename='BackgroundTaskFinished')
router.register('background-tasks/(?P<queue_name>[\w-]+)/started', views.BackgroundTaskStartedViewSet, basename='BackgroundTaskStarted')

app_name = 'core-api'
urlpatterns = router.urls
