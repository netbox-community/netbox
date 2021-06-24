from django.urls import path

from extras import models, views


app_name = 'extras'
urlpatterns = [

    # Custom fields
    path('custom-fields/', views.CustomFieldListView.as_view(), name='customfield_list'),
    path('custom-fields/add/', views.CustomFieldEditView.as_view(), name='customfield_add'),
    path('custom-fields/import/', views.CustomFieldBulkImportView.as_view(), name='customfield_import'),
    path('custom-fields/edit/', views.CustomFieldBulkEditView.as_view(), name='customfield_bulk_edit'),
    path('custom-fields/delete/', views.CustomFieldBulkDeleteView.as_view(), name='customfield_bulk_delete'),
    path('custom-fields/<int:pk>/', views.CustomFieldView.as_view(), name='customfield'),
    path('custom-fields/<int:pk>/edit/', views.CustomFieldEditView.as_view(), name='customfield_edit'),
    path('custom-fields/<int:pk>/delete/', views.CustomFieldDeleteView.as_view(), name='customfield_delete'),
    path('custom-fields/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='customfield_changelog',
         kwargs={'model': models.CustomField}),

    # Custom links
    path('custom-links/', views.CustomLinkListView.as_view(), name='customlink_list'),
    path('custom-links/add/', views.CustomLinkEditView.as_view(), name='customlink_add'),
    path('custom-links/import/', views.CustomLinkBulkImportView.as_view(), name='customlink_import'),
    path('custom-links/edit/', views.CustomLinkBulkEditView.as_view(), name='customlink_bulk_edit'),
    path('custom-links/delete/', views.CustomLinkBulkDeleteView.as_view(), name='customlink_bulk_delete'),
    path('custom-links/<int:pk>/', views.CustomLinkView.as_view(), name='customlink'),
    path('custom-links/<int:pk>/edit/', views.CustomLinkEditView.as_view(), name='customlink_edit'),
    path('custom-links/<int:pk>/delete/', views.CustomLinkDeleteView.as_view(), name='customlink_delete'),
    path('custom-links/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='customlink_changelog',
         kwargs={'model': models.CustomLink}),

    # Export templates
    path('export-templates/', views.ExportTemplateListView.as_view(), name='exporttemplate_list'),
    path('export-templates/add/', views.ExportTemplateEditView.as_view(), name='exporttemplate_add'),
    path('export-templates/import/', views.ExportTemplateBulkImportView.as_view(), name='exporttemplate_import'),
    path('export-templates/edit/', views.ExportTemplateBulkEditView.as_view(), name='exporttemplate_bulk_edit'),
    path('export-templates/delete/', views.ExportTemplateBulkDeleteView.as_view(), name='exporttemplate_bulk_delete'),
    path('export-templates/<int:pk>/', views.ExportTemplateView.as_view(), name='exporttemplate'),
    path('export-templates/<int:pk>/edit/', views.ExportTemplateEditView.as_view(), name='exporttemplate_edit'),
    path('export-templates/<int:pk>/delete/', views.ExportTemplateDeleteView.as_view(), name='exporttemplate_delete'),
    path('export-templates/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='exporttemplate_changelog',
         kwargs={'model': models.ExportTemplate}),

    # Tags
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/add/', views.TagEditView.as_view(), name='tag_add'),
    path('tags/import/', views.TagBulkImportView.as_view(), name='tag_import'),
    path('tags/edit/', views.TagBulkEditView.as_view(), name='tag_bulk_edit'),
    path('tags/delete/', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'),
    path('tags/<int:pk>/edit/', views.TagEditView.as_view(), name='tag_edit'),
    path('tags/<int:pk>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    path('tags/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='tag_changelog',
         kwargs={'model': models.Tag}),

    # Config contexts
    path('config-contexts/', views.ConfigContextListView.as_view(), name='configcontext_list'),
    path('config-contexts/add/', views.ConfigContextEditView.as_view(), name='configcontext_add'),
    path('config-contexts/edit/', views.ConfigContextBulkEditView.as_view(), name='configcontext_bulk_edit'),
    path('config-contexts/delete/', views.ConfigContextBulkDeleteView.as_view(), name='configcontext_bulk_delete'),
    path('config-contexts/<int:pk>/', views.ConfigContextView.as_view(), name='configcontext'),
    path('config-contexts/<int:pk>/edit/', views.ConfigContextEditView.as_view(), name='configcontext_edit'),
    path('config-contexts/<int:pk>/delete/', views.ConfigContextDeleteView.as_view(), name='configcontext_delete'),
    path('config-contexts/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='configcontext_changelog',
         kwargs={'model': models.ConfigContext}),

    # Image attachments
    path('image-attachments/<int:pk>/edit/', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    path('image-attachments/<int:pk>/delete/', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Journal entries
    path('journal-entries/', views.JournalEntryListView.as_view(), name='journalentry_list'),
    path('journal-entries/add/', views.JournalEntryEditView.as_view(), name='journalentry_add'),
    path('journal-entries/edit/', views.JournalEntryBulkEditView.as_view(), name='journalentry_bulk_edit'),
    path('journal-entries/delete/', views.JournalEntryBulkDeleteView.as_view(), name='journalentry_bulk_delete'),
    path('journal-entries/<int:pk>/', views.JournalEntryView.as_view(), name='journalentry'),
    path('journal-entries/<int:pk>/edit/', views.JournalEntryEditView.as_view(), name='journalentry_edit'),
    path('journal-entries/<int:pk>/delete/', views.JournalEntryDeleteView.as_view(), name='journalentry_delete'),
    path('journal-entries/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='journalentry_changelog',
         kwargs={'model': models.JournalEntry}),

    # Change logging
    path('changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path('changelog/<int:pk>/', views.ObjectChangeView.as_view(), name='objectchange'),

    # Reports
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<str:module>.<str:name>/', views.ReportView.as_view(), name='report'),
    path('reports/results/<int:job_result_pk>/', views.ReportResultView.as_view(), name='report_result'),

    # Scripts
    path('scripts/', views.ScriptListView.as_view(), name='script_list'),
    path('scripts/<str:module>.<str:name>/', views.ScriptView.as_view(), name='script'),
    path('scripts/results/<int:job_result_pk>/', views.ScriptResultView.as_view(), name='script_result'),

]
