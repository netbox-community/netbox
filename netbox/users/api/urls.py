from django.urls import include, path

from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.APIRootView = views.UsersRootView

router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)
router.register('tokens', views.TokenViewSet)
router.register('permissions', views.ObjectPermissionViewSet)
router.register('owner-groups', views.OwnerGroupViewSet)
router.register('owners', views.OwnerViewSet)
router.register('config', views.UserConfigViewSet, basename='userconfig')

app_name = 'users-api'
urlpatterns = [
    path('tokens/provision/', views.TokenProvisionView.as_view(), name='token_provision'),
    path('', include(router.urls)),
]
