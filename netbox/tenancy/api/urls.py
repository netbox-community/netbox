from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.TenancyRootView

# Tenants
router.register('tenant-groups', views.TenantGroupViewSet)
router.register('tenants', views.TenantViewSet)

app_name = 'tenancy-api'
urlpatterns = router.urls
