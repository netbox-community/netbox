from django.urls import include, path, re_path

from extras import views
from utilities.urls import get_model_urls


app_name = 'extras'
urlpatterns = [

    # Custom fields
    path('custom-fields/', views.CustomFieldListView.as_view(), name='customfield_list'),
    path('custom-fields/add/', views.CustomFieldEditView.as_view(), name='customfield_add'),
    path('custom-fields/import/', views.CustomFieldBulkImportView.as_view(), name='customfield_import'),
    path('custom-fields/edit/', views.CustomFieldBulkEditView.as_view(), name='customfield_bulk_edit'),
    path('custom-fields/delete/', views.CustomFieldBulkDeleteView.as_view(), name='customfield_bulk_delete'),
    path('custom-fields/<int:pk>/', include(get_model_urls('extras', 'customfield'))),

    # Custom links
    path('custom-links/', views.CustomLinkListView.as_view(), name='customlink_list'),
    path('custom-links/add/', views.CustomLinkEditView.as_view(), name='customlink_add'),
    path('custom-links/import/', views.CustomLinkBulkImportView.as_view(), name='customlink_import'),
    path('custom-links/edit/', views.CustomLinkBulkEditView.as_view(), name='customlink_bulk_edit'),
    path('custom-links/delete/', views.CustomLinkBulkDeleteView.as_view(), name='customlink_bulk_delete'),
    path('custom-links/<int:pk>/', include(get_model_urls('extras', 'customlink'))),

    # Export templates
    path('export-templates/', views.ExportTemplateListView.as_view(), name='exporttemplate_list'),
    path('export-templates/add/', views.ExportTemplateEditView.as_view(), name='exporttemplate_add'),
    path('export-templates/import/', views.ExportTemplateBulkImportView.as_view(), name='exporttemplate_import'),
    path('export-templates/edit/', views.ExportTemplateBulkEditView.as_view(), name='exporttemplate_bulk_edit'),
    path('export-templates/delete/', views.ExportTemplateBulkDeleteView.as_view(), name='exporttemplate_bulk_delete'),
    path('export-templates/<int:pk>/', include(get_model_urls('extras', 'exporttemplate'))),

    # Saved filters
    path('saved-filters/', views.SavedFilterListView.as_view(), name='savedfilter_list'),
    path('saved-filters/add/', views.SavedFilterEditView.as_view(), name='savedfilter_add'),
    path('saved-filters/import/', views.SavedFilterBulkImportView.as_view(), name='savedfilter_import'),
    path('saved-filters/edit/', views.SavedFilterBulkEditView.as_view(), name='savedfilter_bulk_edit'),
    path('saved-filters/delete/', views.SavedFilterBulkDeleteView.as_view(), name='savedfilter_bulk_delete'),
    path('saved-filters/<int:pk>/', include(get_model_urls('extras', 'savedfilter'))),

    # Webhooks
    path('webhooks/', views.WebhookListView.as_view(), name='webhook_list'),
    path('webhooks/add/', views.WebhookEditView.as_view(), name='webhook_add'),
    path('webhooks/import/', views.WebhookBulkImportView.as_view(), name='webhook_import'),
    path('webhooks/edit/', views.WebhookBulkEditView.as_view(), name='webhook_bulk_edit'),
    path('webhooks/delete/', views.WebhookBulkDeleteView.as_view(), name='webhook_bulk_delete'),
    path('webhooks/<int:pk>/', include(get_model_urls('extras', 'webhook'))),

    # Tags
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/add/', views.TagEditView.as_view(), name='tag_add'),
    path('tags/import/', views.TagBulkImportView.as_view(), name='tag_import'),
    path('tags/edit/', views.TagBulkEditView.as_view(), name='tag_bulk_edit'),
    path('tags/delete/', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),
    path('tags/<int:pk>/', include(get_model_urls('extras', 'tag'))),

    # Config contexts
    path('config-contexts/', views.ConfigContextListView.as_view(), name='configcontext_list'),
    path('config-contexts/add/', views.ConfigContextEditView.as_view(), name='configcontext_add'),
    path('config-contexts/edit/', views.ConfigContextBulkEditView.as_view(), name='configcontext_bulk_edit'),
    path('config-contexts/delete/', views.ConfigContextBulkDeleteView.as_view(), name='configcontext_bulk_delete'),
    path('config-contexts/<int:pk>/', include(get_model_urls('extras', 'configcontext'))),

    # Image attachments
    path('image-attachments/add/', views.ImageAttachmentEditView.as_view(), name='imageattachment_add'),
    path('image-attachments/<int:pk>/', include(get_model_urls('extras', 'imageattachment'))),

    # Journal entries
    path('journal-entries/', views.JournalEntryListView.as_view(), name='journalentry_list'),
    path('journal-entries/add/', views.JournalEntryEditView.as_view(), name='journalentry_add'),
    path('journal-entries/edit/', views.JournalEntryBulkEditView.as_view(), name='journalentry_bulk_edit'),
    path('journal-entries/delete/', views.JournalEntryBulkDeleteView.as_view(), name='journalentry_bulk_delete'),
    path('journal-entries/<int:pk>/', include(get_model_urls('extras', 'journalentry'))),

    # Change logging
    path('changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path('changelog/<int:pk>/', include(get_model_urls('extras', 'objectchange'))),

    # Reports
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/results/<int:job_result_pk>/', views.ReportResultView.as_view(), name='report_result'),
    re_path(r'^reports/(?P<module>.([^.]+)).(?P<name>.(.+))/', views.ReportView.as_view(), name='report'),

    # Job results
    path('job-results/', views.JobResultListView.as_view(), name='jobresult_list'),
    path('job-results/delete/', views.JobResultBulkDeleteView.as_view(), name='jobresult_bulk_delete'),
    path('job-results/<int:pk>/delete/', views.JobResultDeleteView.as_view(), name='jobresult_delete'),

    # Scripts
    path('scripts/', views.ScriptListView.as_view(), name='script_list'),
    path('scripts/results/<int:job_result_pk>/', views.ScriptResultView.as_view(), name='script_result'),
    re_path(r'^scripts/(?P<module>.([^.]+)).(?P<name>.(.+))/', views.ScriptView.as_view(), name='script'),

    # Markdown
    path('render/markdown/', views.RenderMarkdownView.as_view(), name="render_markdown")
]
