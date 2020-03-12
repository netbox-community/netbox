from rest_framework import routers

from . import views


class SecretsRootView(routers.APIRootView):
    """
    Secrets API root view
    """
    def get_view_name(self):
        return 'Secrets'


router = routers.DefaultRouter()
router.APIRootView = SecretsRootView

# Secrets
router.register('secret-roles', views.SecretRoleViewSet)
router.register('secrets', views.SecretViewSet)

# Miscellaneous
router.register('get-session-key', views.GetSessionKeyViewSet, basename='get-session-key')
router.register('generate-rsa-key-pair', views.GenerateRSAKeyPairViewSet, basename='generate-rsa-key-pair')

app_name = 'secrets-api'
urlpatterns = router.urls
