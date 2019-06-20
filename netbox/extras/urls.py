from django.urls import path

from extras import views
from extras.models import Tag


app_name = 'extras'
urlpatterns = [

    # Tags
    path(r'tags/', views.TagListView.as_view(), name='tag_list'),
    path(r'tags/delete/', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),
    path(r'tags/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path(r'tags/<slug:slug>/edit/', views.TagEditView.as_view(), name='tag_edit'),
    path(r'tags/<slug:slug>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    path(r'tags/<slug:slug>/changelog/', views.ObjectChangeLogView.as_view(), name='tag_changelog', kwargs={'model': Tag}),

    # Config contexts
    path(r'config-contexts/', views.ConfigContextListView.as_view(), name='configcontext_list'),
    path(r'config-contexts/add/', views.ConfigContextCreateView.as_view(), name='configcontext_add'),
    path(r'config-contexts/edit/', views.ConfigContextBulkEditView.as_view(), name='configcontext_bulk_edit'),
    path(r'config-contexts/delete/', views.ConfigContextBulkDeleteView.as_view(), name='configcontext_bulk_delete'),
    path(r'config-contexts/<int:pk>/', views.ConfigContextView.as_view(), name='configcontext'),
    path(r'config-contexts/<int:pk>/edit/', views.ConfigContextEditView.as_view(), name='configcontext_edit'),
    path(r'config-contexts/<int:pk>/delete/', views.ConfigContextDeleteView.as_view(), name='configcontext_delete'),

    # Image attachments
    path(r'image-attachments/<int:pk>/edit/', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    path(r'image-attachments/<int:pk>/delete/', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Reports
    path(r'reports/', views.ReportListView.as_view(), name='report_list'),
    path(r'reports/<str:name>/', views.ReportView.as_view(), name='report'),
    path(r'reports/<str:name>/run/', views.ReportRunView.as_view(), name='report_run'),

    # Change logging
    path(r'changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path(r'changelog/<int:pk>/', views.ObjectChangeView.as_view(), name='objectchange'),

]
