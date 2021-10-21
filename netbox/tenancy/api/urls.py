from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.TenancyRootView

# Tenants
router.register('tenant-groups', views.TenantGroupViewSet)
router.register('tenants', views.TenantViewSet)

# Contacts
router.register('contact-groups', views.ContactGroupViewSet)
router.register('contact-roles', views.ContactRoleViewSet)
router.register('contacts', views.ContactViewSet)
router.register('contact-assignments', views.ContactAssignmentViewSet)

app_name = 'tenancy-api'
urlpatterns = router.urls
