from rest_framework import routers

from . import views


class VirtualizationRootView(routers.APIRootView):
    """
    Virtualization API root view
    """
    def get_view_name(self):
        return 'Virtualization'


router = routers.DefaultRouter()
router.APIRootView = VirtualizationRootView

# Field choices
router.register('_choices', views.VirtualizationFieldChoicesViewSet, basename='field-choice')

# Clusters
router.register('cluster-types', views.ClusterTypeViewSet)
router.register('cluster-groups', views.ClusterGroupViewSet)
router.register('clusters', views.ClusterViewSet)

# VirtualMachines
router.register('virtual-machines', views.VirtualMachineViewSet)
router.register('interfaces', views.InterfaceViewSet)

app_name = 'virtualization-api'
urlpatterns = router.urls
