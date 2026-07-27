from django.urls import include, path
from rest_framework.routers import Route

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


class ScriptRouter(NetBoxRouter):
    """
    Router variant that extends the detail route's mapping to include
    POST, so ScriptViewSet.post() (running a script) is dispatched
    through the same router-generated detail URL as retrieve/update/
    partial_update/destroy, rather than a separately hand-written path().
    """
    routes = NetBoxRouter.routes.copy()
    _new_routes = []
    for _route in routes:
        if isinstance(_route, Route) and _route.mapping.get('get') == 'retrieve':
            _mapping = dict(_route.mapping)
            _mapping['post'] = 'post'
            _route = _route._replace(mapping=_mapping)
        _new_routes.append(_route)
    routes = _new_routes


script_router = ScriptRouter()
script_router.register('scripts', views.ScriptViewSet, basename='script')

app_name = 'extras-api'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
    path('', include(script_router.urls)),
]
