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

urlpatterns = (
    path('background-queues/', views.QueueListView.as_view()),
    path('background-workers/', views.WorkerListView.as_view()),
    path('background-workers/<str:worker_name>/', views.WorkerDetailView.as_view()),
    path('background-tasks/<str:queue_name>/', views.TaskListView.as_view()),
    path('background-tasks/<str:queue_name>/deferred/', views.DeferredTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/failed/', views.FailedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/finished/', views.FinishedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/started/', views.StartedTaskListView.as_view()),
    path('background-tasks/<str:queue_name>/queued/', views.QueuedTaskListView.as_view()),
    path('background-task/<str:task_id>/', views.TaskDetailView.as_view()),
    path('background-task/<str:task_id>/delete/', views.TaskDeleteView.as_view()),
    path('background-task/<str:task_id>/requeue/', views.TaskRequeueView.as_view()),
    path('background-task/<str:task_id>/enqueue/', views.TaskEnqueueView.as_view()),
    path('background-task/<str:task_id>/stop/', views.TaskStopView.as_view()),

    path('', include(router.urls)),
)
