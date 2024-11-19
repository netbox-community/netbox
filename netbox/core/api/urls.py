from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'core-api'

router = NetBoxRouter()
router.APIRootView = views.CoreRootView

router.register('data-sources', views.DataSourceViewSet)
router.register('data-files', views.DataFileViewSet)
router.register('jobs', views.JobViewSet)
router.register('object-changes', views.ObjectChangeViewSet)
router.register('background-queues', views.QueueViewSet, basename='rqqueue')
router.register('background-workers', views.WorkerViewSet, basename='rqworker')
router.register('background-tasks/(?P<queue_name>.+)/', views.TaskViewSet, basename='rqtask')
router.register('background-task', views.TaskDetailViewSet, basename='rqtaskdetail')

urlpatterns = router.urls
