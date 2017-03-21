from rest_framework import routers

from . import views


class TenancyRootView(routers.APIRootView):
    """
    Tenancy API root view
    """
    def get_view_name(self):
        return 'Tenancy'


router = routers.DefaultRouter()
router.APIRootView = TenancyRootView

# Tenants
router.register(r'tenant-groups', views.TenantGroupViewSet)
router.register(r'tenants', views.TenantViewSet)

urlpatterns = router.urls
