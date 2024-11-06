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


# Background Tasks
"""
router.register('background-queues/', views.BackgroundQueueListView.as_view(), name='background_queue_list'),
router.register('background-queues/<int:queue_index>/<str:status>/', views.BackgroundTaskListView.as_view(), name='background_task_list'),
router.register('background-tasks/<str:job_id>/', views.BackgroundTaskView.as_view(), name='background_task'),
router.register('background-tasks/<str:job_id>/delete/', views.BackgroundTaskDeleteView.as_view(), name='background_task_delete'),
router.register('background-tasks/<str:job_id>/requeue/', views.BackgroundTaskRequeueView.as_view(), name='background_task_requeue'),
router.register('background-tasks/<str:job_id>/enqueue/', views.BackgroundTaskEnqueueView.as_view(), name='background_task_enqueue'),
router.register('background-tasks/<str:job_id>/stop/', views.BackgroundTaskStopView.as_view(), name='background_task_stop'),
router.register('background-workers/<int:queue_index>/', views.WorkerListView.as_view(), name='worker_list'),
router.register('background-workers/<str:key>/', views.WorkerView.as_view(), name='worker'),
"""

urlpatterns = (
    path('background-queues/', views.QueueListView.as_view()),
    path('background-workers/', views.WorkerListView.as_view()),
    # path('background-workers/<str:key>/', views.WorkerView.as_view()),
    path('background-tasks/<str:queue_name>/', views.TaskListView.as_view()),
    path('background-tasks/<str:queue_name>/deferred/', views.DeferredTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/failed/', views.FailedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/finished/', views.FinishedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/started/', views.StartedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/queued/', views.QueuedTaskListView.as_view()),
    # path('background-tasks/<str:queue_name>/workers', views.BackgroundWorkerListView.as_view()),

    path('', include(router.urls)),
)
