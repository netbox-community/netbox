from django.conf.urls import include, url

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'secret-roles', views.SecretRoleViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Secrets
    url(r'^secrets/$', views.SecretListView.as_view(), name='secret_list'),
    url(r'^secrets/(?P<pk>\d+)/$', views.SecretDetailView.as_view(), name='secret_detail'),

    # Miscellaneous
    url(r'^generate-keys/$', views.RSAKeyGeneratorView.as_view(), name='generate_keys'),

]
