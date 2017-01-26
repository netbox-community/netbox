from django.conf.urls import include, url

from rest_framework import routers

from .views import (

    # Viewsets
    SecretRoleViewSet,

    # Legacy views
    RSAKeyGeneratorView, SecretDetailView, SecretListView,

)


router = routers.DefaultRouter()
router.register(r'secret-roles', SecretRoleViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Secrets
    url(r'^secrets/$', SecretListView.as_view(), name='secret_list'),
    url(r'^secrets/(?P<pk>\d+)/$', SecretDetailView.as_view(), name='secret_detail'),

    # Miscellaneous
    url(r'^generate-keys/$', RSAKeyGeneratorView.as_view(), name='generate_keys'),

]
