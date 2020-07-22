from rest_framework import routers

from . import views


class UsersRootView(routers.APIRootView):
    """
    Users API root view
    """
    def get_view_name(self):
        return 'Users'


router = routers.DefaultRouter()
router.APIRootView = UsersRootView

# Users and groups
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)

# Permissions
router.register('permissions', views.ObjectPermissionViewSet)

app_name = 'users-api'
urlpatterns = router.urls
