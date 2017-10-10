from __future__ import unicode_literals

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

# Field choices
router.register(r'_choices', views.SecretsFieldChoicesViewSet, base_name='field-choice')

# Secrets
router.register(r'secret-roles', views.SecretRoleViewSet)
router.register(r'secrets', views.SecretViewSet)

# Miscellaneous
router.register(r'get-session-key', views.GetSessionKeyViewSet, base_name='get-session-key')
router.register(r'generate-rsa-key-pair', views.GenerateRSAKeyPairViewSet, base_name='generate-rsa-key-pair')

app_name = 'secrets-api'
urlpatterns = router.urls
