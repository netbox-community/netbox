from __future__ import unicode_literals

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
router.register(r'_choices', views.VirtualizationFieldChoicesViewSet, base_name='field-choice')

# Clusters
router.register(r'cluster-types', views.ClusterTypeViewSet)
router.register(r'cluster-groups', views.ClusterGroupViewSet)
router.register(r'clusters', views.ClusterViewSet)

# VirtualMachines
router.register(r'virtual-machines', views.VirtualMachineViewSet)
router.register(r'interfaces', views.InterfaceViewSet)

app_name = 'virtualization-api'
urlpatterns = router.urls
