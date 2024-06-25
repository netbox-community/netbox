from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'core'
urlpatterns = (

    # Data sources
    path('data-sources/', views.DataSourceListView.as_view(), name='datasource_list'),
    path('data-sources/add/', views.DataSourceEditView.as_view(), name='datasource_add'),
    path('data-sources/import/', views.DataSourceBulkImportView.as_view(), name='datasource_import'),
    path('data-sources/edit/', views.DataSourceBulkEditView.as_view(), name='datasource_bulk_edit'),
    path('data-sources/delete/', views.DataSourceBulkDeleteView.as_view(), name='datasource_bulk_delete'),
    path('data-sources/<int:pk>/', include(get_model_urls('core', 'datasource'))),

    # Data files
    path('data-files/', views.DataFileListView.as_view(), name='datafile_list'),
    path('data-files/delete/', views.DataFileBulkDeleteView.as_view(), name='datafile_bulk_delete'),
    path('data-files/<int:pk>/', include(get_model_urls('core', 'datafile'))),

    # Job results
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/delete/', views.JobBulkDeleteView.as_view(), name='job_bulk_delete'),
    path('jobs/<int:pk>/', views.JobView.as_view(), name='job'),
    path('jobs/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),

    # Change logging
    path('changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path('changelog/<int:pk>/', include(get_model_urls('core', 'objectchange'))),

    # Background Tasks
    path('background-queues/', views.BackgroundQueueListView.as_view(), name='background_queue_list'),
    path('background-queues/<int:queue_index>/<str:status>/', views.BackgroundTaskListView.as_view(), name='background_task_list'),
    path('background-tasks/<str:job_id>/', views.BackgroundTaskView.as_view(), name='background_task'),
    path('background-tasks/<str:job_id>/delete/', views.BackgroundTaskDeleteView.as_view(), name='background_task_delete'),
    path('background-tasks/<str:job_id>/requeue/', views.BackgroundTaskRequeueView.as_view(), name='background_task_requeue'),
    path('background-tasks/<str:job_id>/enqueue/', views.BackgroundTaskEnqueueView.as_view(), name='background_task_enqueue'),
    path('background-tasks/<str:job_id>/stop/', views.BackgroundTaskStopView.as_view(), name='background_task_stop'),
    path('background-workers/<int:queue_index>/', views.WorkerListView.as_view(), name='worker_list'),
    path('background-workers/<str:key>/', views.WorkerView.as_view(), name='worker'),

    # Config revisions
    path('config-revisions/', views.ConfigRevisionListView.as_view(), name='configrevision_list'),
    path('config-revisions/add/', views.ConfigRevisionEditView.as_view(), name='configrevision_add'),
    path('config-revisions/delete/', views.ConfigRevisionBulkDeleteView.as_view(), name='configrevision_bulk_delete'),
    path('config-revisions/<int:pk>/restore/', views.ConfigRevisionRestoreView.as_view(), name='configrevision_restore'),
    path('config-revisions/<int:pk>/', include(get_model_urls('core', 'configrevision'))),

    # System
    path('system/', views.SystemView.as_view(), name='system'),
)
