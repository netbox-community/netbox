from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.ExtrasRootView

# Webhooks
router.register('webhooks', views.WebhookViewSet)

# Custom fields
router.register('custom-fields', views.CustomFieldViewSet)

# Custom links
router.register('custom-links', views.CustomLinkViewSet)

# Export templates
router.register('export-templates', views.ExportTemplateViewSet)

# Tags
router.register('tags', views.TagViewSet)

# Image attachments
router.register('image-attachments', views.ImageAttachmentViewSet)

# Journal entries
router.register('journal-entries', views.JournalEntryViewSet)

# Config contexts
router.register('config-contexts', views.ConfigContextViewSet)

# Reports
router.register('reports', views.ReportViewSet, basename='report')

# Scripts
router.register('scripts', views.ScriptViewSet, basename='script')

# Change logging
router.register('object-changes', views.ObjectChangeViewSet)

# Job Results
router.register('job-results', views.JobResultViewSet)

# ContentTypes
router.register('content-types', views.ContentTypeViewSet)

app_name = 'extras-api'
urlpatterns = router.urls
