from django.urls import include, path

from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.ExtrasRootView

router.register('event-rules', views.EventRuleViewSet)
router.register('webhooks', views.WebhookViewSet)
router.register('custom-fields', views.CustomFieldViewSet)
router.register('custom-field-choice-sets', views.CustomFieldChoiceSetViewSet)
router.register('custom-links', views.CustomLinkViewSet)
router.register('export-templates', views.ExportTemplateViewSet)
router.register('saved-filters', views.SavedFilterViewSet)
router.register('bookmarks', views.BookmarkViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('notification-groups', views.NotificationGroupViewSet)
router.register('subscriptions', views.SubscriptionViewSet)
router.register('tags', views.TagViewSet)
router.register('image-attachments', views.ImageAttachmentViewSet)
router.register('journal-entries', views.JournalEntryViewSet)
router.register('config-contexts', views.ConfigContextViewSet)
router.register('config-templates', views.ConfigTemplateViewSet)
router.register('scripts', views.ScriptViewSet, basename='script')
router.register('object-types', views.ObjectTypeViewSet)

app_name = 'extras-api'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
