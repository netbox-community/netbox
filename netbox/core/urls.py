from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'core'
urlpatterns = (

    path('data-sources/', include(get_model_urls('core', 'datasource', detail=False))),
    path('data-sources/<int:pk>/', include(get_model_urls('core', 'datasource'))),

    path('data-files/', include(get_model_urls('core', 'datafile', detail=False))),
    path('data-files/<int:pk>/', include(get_model_urls('core', 'datafile'))),

    path('jobs/', include(get_model_urls('core', 'job', detail=False))),
    path('jobs/<int:pk>/', include(get_model_urls('core', 'job'))),

    path('changelog/', include(get_model_urls('core', 'objectchange', detail=False))),
    path('changelog/<int:pk>/', include(get_model_urls('core', 'objectchange'))),

    # Background Tasks
    path('background-queues/', views.BackgroundQueueListView.as_view(), name='background_queue_list'),
    path(
        'background-queues/<int:queue_index>/<str:status>/',
        views.BackgroundTaskListView.as_view(),
        name='background_task_list'
    ),
    path('background-tasks/<str:job_id>/', views.BackgroundTaskView.as_view(), name='background_task'),
    path(
        'background-tasks/<str:job_id>/delete/',
        views.BackgroundTaskDeleteView.as_view(),
        name='background_task_delete'
    ),
    path(
        'background-tasks/<str:job_id>/requeue/',
        views.BackgroundTaskRequeueView.as_view(),
        name='background_task_requeue'
    ),
    path(
        'background-tasks/<str:job_id>/enqueue/',
        views.BackgroundTaskEnqueueView.as_view(),
        name='background_task_enqueue'
    ),
    path('background-tasks/<str:job_id>/stop/', views.BackgroundTaskStopView.as_view(), name='background_task_stop'),
    path('background-workers/<int:queue_index>/', views.WorkerListView.as_view(), name='worker_list'),
    path('background-workers/<str:key>/', views.WorkerView.as_view(), name='worker'),

    path('config-revisions/', include(get_model_urls('core', 'configrevision', detail=False))),
    path('config-revisions/<int:pk>/', include(get_model_urls('core', 'configrevision'))),

    path('system/', views.SystemView.as_view(), name='system'),

    path('plugins/', views.PluginListView.as_view(), name='plugin_list'),
    path('plugins/<str:name>/', views.PluginView.as_view(), name='plugin'),
)
