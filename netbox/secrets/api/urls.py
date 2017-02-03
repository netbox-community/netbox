from django.conf.urls import include, url

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'secret-roles', views.SecretRoleViewSet)
router.register(r'secrets', views.SecretViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Miscellaneous
    url(r'^get-session-key/$', views.GetSessionKey.as_view(), name='get_session_key'),
    url(r'^generate-keys/$', views.RSAKeyGeneratorView.as_view(), name='generate_keys'),

]
