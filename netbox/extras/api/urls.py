from rest_framework import routers

from . import views


class ExtrasRootView(routers.APIRootView):
    """
    Extras API root view
    """
    def get_view_name(self):
        return 'Extras'


router = routers.DefaultRouter()
router.APIRootView = ExtrasRootView

# Field choices
router.register(r'_choices', views.ExtrasFieldChoicesViewSet, basename='field-choice')

# Custom field choices
router.register(r'_custom_field_choices', views.CustomFieldChoicesViewSet, base_name='custom-field-choice')

# Graphs
router.register(r'graphs', views.GraphViewSet)

# Export templates
router.register(r'export-templates', views.ExportTemplateViewSet)

# Topology maps
router.register(r'topology-maps', views.TopologyMapViewSet)

# Tags
router.register(r'tags', views.TagViewSet)

# Image attachments
router.register(r'image-attachments', views.ImageAttachmentViewSet)

# Config contexts
router.register(r'config-contexts', views.ConfigContextViewSet)

# Reports
router.register(r'reports', views.ReportViewSet, basename='report')

# Change logging
router.register(r'object-changes', views.ObjectChangeViewSet)

app_name = 'extras-api'
urlpatterns = router.urls
