from django.urls import path, include

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

urlpatterns = (
    path('background-task/<str:task_id>/', views.TaskDetailView.as_view(), name="background_task_detail"),
    path('background-task/<str:task_id>/delete/', views.TaskDeleteView.as_view(), name="background_task_delete"),
    path('background-task/<str:task_id>/requeue/', views.TaskRequeueView.as_view(), name="background_task_requeue"),
    path('background-task/<str:task_id>/enqueue/', views.TaskEnqueueView.as_view(), name="background_task_enqueue"),
    path('background-task/<str:task_id>/stop/', views.TaskStopView.as_view(), name="background_task_stop"),

    path('', include(router.urls)),
)
