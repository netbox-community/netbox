from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.UsersRootView

# Users and groups
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)

# Permissions
router.register('permissions', views.ObjectPermissionViewSet)

# User preferences
router.register('config', views.UserConfigViewSet, basename='userconfig')

app_name = 'users-api'
urlpatterns = router.urls
