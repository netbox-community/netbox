from django.urls import include, path

from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.UsersRootView

# Users and groups
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)

# Tokens
router.register('tokens', views.TokenViewSet)

# Permissions
router.register('permissions', views.ObjectPermissionViewSet)

# User preferences
router.register('config', views.UserConfigViewSet, basename='userconfig')

app_name = 'users-api'
urlpatterns = [
    path('tokens/provision/', views.TokenProvisionView.as_view(), name='token_provision'),
    path('', include(router.urls)),
]
