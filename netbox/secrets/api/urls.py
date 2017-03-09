from rest_framework import routers

from . import views


router = routers.DefaultRouter()

# Secrets
router.register(r'secret-roles', views.SecretRoleViewSet)
router.register(r'secrets', views.SecretViewSet)

# Miscellaneous
router.register(r'get-session-key', views.GetSessionKeyViewSet, base_name='get-session-key')
router.register(r'generate-rsa-key-pair', views.GenerateRSAKeyPairViewSet, base_name='generate-rsa-key-pair')

urlpatterns = router.urls
