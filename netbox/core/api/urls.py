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
    # path('background-tasks/<str:queue_name>/', views.TaskListView.as_view(), name="background_task_list"),
    # path('background-tasks/<str:queue_name>/deferred/', views.DeferredTaskListView.as_view(), name="background_tasks_deferred"),
    # path('background-tasks/<str:queue_name>/failed/', views.FailedTaskListView.as_view(), name="background_tasks_failed"),
    # path('background-tasks/<str:queue_name>/finished/', views.FinishedTaskListView.as_view(), name="background_tasks_finished"),
    # path('background-tasks/<str:queue_name>/started/', views.StartedTaskListView.as_view(), name="background_tasks_started"),
    # path('background-tasks/<str:queue_name>/queued/', views.QueuedTaskListView.as_view(), name="background_tasks_queued"),
    path('background-task/<str:task_id>/', views.TaskDetailView.as_view(), name="background_task_detail"),
    path('background-task/<str:task_id>/delete/', views.TaskDeleteView.as_view(), name="background_task_delete"),
    path('background-task/<str:task_id>/requeue/', views.TaskRequeueView.as_view(), name="background_task_requeue"),
    path('background-task/<str:task_id>/enqueue/', views.TaskEnqueueView.as_view(), name="background_task_enqueue"),
    path('background-task/<str:task_id>/stop/', views.TaskStopView.as_view(), name="background_task_stop"),

    path('', include(router.urls)),
)
