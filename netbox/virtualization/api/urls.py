from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.VirtualizationRootView

# Clusters
router.register('cluster-types', views.ClusterTypeViewSet)
router.register('cluster-groups', views.ClusterGroupViewSet)
router.register('clusters', views.ClusterViewSet)

# VirtualMachines
router.register('virtual-machines', views.VirtualMachineViewSet)
router.register('interfaces', views.VMInterfaceViewSet)

app_name = 'virtualization-api'
urlpatterns = router.urls
