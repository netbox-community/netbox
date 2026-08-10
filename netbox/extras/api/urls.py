from django.urls import include, path
from rest_framework.routers import Route

from netbox.api.routers import NetBoxRouter

from . import views


class ExtrasRouter(NetBoxRouter):
    """
    Extend NetBoxRouter to map additional HTTP methods on the detail route to named actions, as declared
    by a ViewSet's `detail_route_mapping` (e.g. ScriptViewSet maps POST to its run() action). DRF's detail
    route maps only the standard CRUD methods; absent this, such a handler must be declared as a raw HTTP
    method (e.g. post()), which is bound to every route of the ViewSet and is invisible to both per-action
    permissions and schema generation.
    """
    def get_routes(self, viewset):
        routes = super().get_routes(viewset)

        if mapping := getattr(viewset, 'detail_route_mapping', None):
            routes = [
                route._replace(mapping={**route.mapping, **mapping})
                if isinstance(route, Route) and route.detail else route
                for route in routes
            ]

        return routes


router = ExtrasRouter()
router.APIRootView = views.ExtrasRootView

router.register('event-rules', views.EventRuleViewSet)
router.register('webhooks', views.WebhookViewSet)
router.register('custom-fields', views.CustomFieldViewSet)
router.register('custom-field-choice-sets', views.CustomFieldChoiceSetViewSet)
router.register('custom-links', views.CustomLinkViewSet)
router.register('export-templates', views.ExportTemplateViewSet)
router.register('saved-filters', views.SavedFilterViewSet)
router.register('table-configs', views.TableConfigViewSet)
router.register('bookmarks', views.BookmarkViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('notification-groups', views.NotificationGroupViewSet)
router.register('subscriptions', views.SubscriptionViewSet)
router.register('tags', views.TagViewSet)
router.register('tagged-objects', views.TaggedItemViewSet)
router.register('image-attachments', views.ImageAttachmentViewSet)
router.register('journal-entries', views.JournalEntryViewSet)
router.register('config-contexts', views.ConfigContextViewSet)
router.register('config-context-profiles', views.ConfigContextProfileViewSet)
router.register('config-templates', views.ConfigTemplateViewSet)
router.register('scripts/upload', views.ScriptModuleViewSet)
router.register('scripts', views.ScriptViewSet, basename='script')

app_name = 'extras-api'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
