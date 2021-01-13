from netbox.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.SecretsRootView

# Secrets
router.register('secret-roles', views.SecretRoleViewSet)
router.register('secrets', views.SecretViewSet)

# Miscellaneous
router.register('get-session-key', views.GetSessionKeyViewSet, basename='get-session-key')
router.register('generate-rsa-key-pair', views.GenerateRSAKeyPairViewSet, basename='generate-rsa-key-pair')

app_name = 'secrets-api'
urlpatterns = router.urls
