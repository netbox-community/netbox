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

)
