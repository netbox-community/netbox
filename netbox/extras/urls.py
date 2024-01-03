from django.urls import include, path

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

    # Custom field choices
    path('custom-field-choices/', views.CustomFieldChoiceSetListView.as_view(), name='customfieldchoiceset_list'),
    path('custom-field-choices/add/', views.CustomFieldChoiceSetEditView.as_view(), name='customfieldchoiceset_add'),
    path('custom-field-choices/import/', views.CustomFieldChoiceSetBulkImportView.as_view(), name='customfieldchoiceset_import'),
    path('custom-field-choices/edit/', views.CustomFieldChoiceSetBulkEditView.as_view(), name='customfieldchoiceset_bulk_edit'),
    path('custom-field-choices/delete/', views.CustomFieldChoiceSetBulkDeleteView.as_view(), name='customfieldchoiceset_bulk_delete'),
    path('custom-field-choices/<int:pk>/', include(get_model_urls('extras', 'customfieldchoiceset'))),

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
    path('export-templates/sync/', views.ExportTemplateBulkSyncDataView.as_view(), name='exporttemplate_bulk_sync'),
    path('export-templates/<int:pk>/', include(get_model_urls('extras', 'exporttemplate'))),

    # Saved filters
    path('saved-filters/', views.SavedFilterListView.as_view(), name='savedfilter_list'),
    path('saved-filters/add/', views.SavedFilterEditView.as_view(), name='savedfilter_add'),
    path('saved-filters/import/', views.SavedFilterBulkImportView.as_view(), name='savedfilter_import'),
    path('saved-filters/edit/', views.SavedFilterBulkEditView.as_view(), name='savedfilter_bulk_edit'),
    path('saved-filters/delete/', views.SavedFilterBulkDeleteView.as_view(), name='savedfilter_bulk_delete'),
    path('saved-filters/<int:pk>/', include(get_model_urls('extras', 'savedfilter'))),

    # Bookmarks
    path('bookmarks/add/', views.BookmarkCreateView.as_view(), name='bookmark_add'),
    path('bookmarks/delete/', views.BookmarkBulkDeleteView.as_view(), name='bookmark_bulk_delete'),
    path('bookmarks/<int:pk>/', include(get_model_urls('extras', 'bookmark'))),

    # Webhooks
    path('webhooks/', views.WebhookListView.as_view(), name='webhook_list'),
    path('webhooks/add/', views.WebhookEditView.as_view(), name='webhook_add'),
    path('webhooks/import/', views.WebhookBulkImportView.as_view(), name='webhook_import'),
    path('webhooks/edit/', views.WebhookBulkEditView.as_view(), name='webhook_bulk_edit'),
    path('webhooks/delete/', views.WebhookBulkDeleteView.as_view(), name='webhook_bulk_delete'),
    path('webhooks/<int:pk>/', include(get_model_urls('extras', 'webhook'))),

    # Event rules
    path('event-rules/', views.EventRuleListView.as_view(), name='eventrule_list'),
    path('event-rules/add/', views.EventRuleEditView.as_view(), name='eventrule_add'),
    path('event-rules/import/', views.EventRuleBulkImportView.as_view(), name='eventrule_import'),
    path('event-rules/edit/', views.EventRuleBulkEditView.as_view(), name='eventrule_bulk_edit'),
    path('event-rules/delete/', views.EventRuleBulkDeleteView.as_view(), name='eventrule_bulk_delete'),
    path('event-rules/<int:pk>/', include(get_model_urls('extras', 'eventrule'))),

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
    path('config-contexts/sync/', views.ConfigContextBulkSyncDataView.as_view(), name='configcontext_bulk_sync'),
    path('config-contexts/<int:pk>/', include(get_model_urls('extras', 'configcontext'))),

    # Config templates
    path('config-templates/', views.ConfigTemplateListView.as_view(), name='configtemplate_list'),
    path('config-templates/add/', views.ConfigTemplateEditView.as_view(), name='configtemplate_add'),
    path('config-templates/edit/', views.ConfigTemplateBulkEditView.as_view(), name='configtemplate_bulk_edit'),
    path('config-templates/delete/', views.ConfigTemplateBulkDeleteView.as_view(), name='configtemplate_bulk_delete'),
    path('config-templates/sync/', views.ConfigTemplateBulkSyncDataView.as_view(), name='configtemplate_bulk_sync'),
    path('config-templates/<int:pk>/', include(get_model_urls('extras', 'configtemplate'))),

    # Image attachments
    path('image-attachments/', views.ImageAttachmentListView.as_view(), name='imageattachment_list'),
    path('image-attachments/add/', views.ImageAttachmentEditView.as_view(), name='imageattachment_add'),
    path('image-attachments/<int:pk>/', include(get_model_urls('extras', 'imageattachment'))),

    # Journal entries
    path('journal-entries/', views.JournalEntryListView.as_view(), name='journalentry_list'),
    path('journal-entries/add/', views.JournalEntryEditView.as_view(), name='journalentry_add'),
    path('journal-entries/edit/', views.JournalEntryBulkEditView.as_view(), name='journalentry_bulk_edit'),
    path('journal-entries/delete/', views.JournalEntryBulkDeleteView.as_view(), name='journalentry_bulk_delete'),
    path('journal-entries/import/', views.JournalEntryBulkImportView.as_view(), name='journalentry_import'),
    path('journal-entries/<int:pk>/', include(get_model_urls('extras', 'journalentry'))),

    # Change logging
    path('changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path('changelog/<int:pk>/', include(get_model_urls('extras', 'objectchange'))),

    # User dashboard
    path('dashboard/reset/', views.DashboardResetView.as_view(), name='dashboard_reset'),
    path('dashboard/widgets/add/', views.DashboardWidgetAddView.as_view(), name='dashboardwidget_add'),
    path('dashboard/widgets/<uuid:id>/configure/', views.DashboardWidgetConfigView.as_view(), name='dashboardwidget_config'),
    path('dashboard/widgets/<uuid:id>/delete/', views.DashboardWidgetDeleteView.as_view(), name='dashboardwidget_delete'),

    # Reports
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/add/', views.ReportModuleCreateView.as_view(), name='reportmodule_add'),
    path('reports/results/<int:job_pk>/', views.ReportResultView.as_view(), name='report_result'),
    path('reports/<int:pk>/', include(get_model_urls('extras', 'reportmodule'))),
    path('reports/<str:module>/<str:name>/', views.ReportView.as_view(), name='report'),
    path('reports/<str:module>/<str:name>/source/', views.ReportSourceView.as_view(), name='report_source'),
    path('reports/<str:module>/<str:name>/jobs/', views.ReportJobsView.as_view(), name='report_jobs'),

    # Scripts
    path('scripts/', views.ScriptListView.as_view(), name='script_list'),
    path('scripts/add/', views.ScriptModuleCreateView.as_view(), name='scriptmodule_add'),
    path('scripts/results/<int:job_pk>/', views.ScriptResultView.as_view(), name='script_result'),
    path('scripts/<int:pk>/', include(get_model_urls('extras', 'scriptmodule'))),
    path('scripts/<str:module>/<str:name>/', views.ScriptView.as_view(), name='script'),
    path('scripts/<str:module>/<str:name>/source/', views.ScriptSourceView.as_view(), name='script_source'),
    path('scripts/<str:module>/<str:name>/jobs/', views.ScriptJobsView.as_view(), name='script_jobs'),

    # Markdown
    path('render/markdown/', views.RenderMarkdownView.as_view(), name="render_markdown"),
]
