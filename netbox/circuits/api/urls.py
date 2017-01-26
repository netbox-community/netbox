from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_PROVIDER
from extras.api.views import GraphListView

from .views import CircuitViewSet, CircuitTypeViewSet, ProviderViewSet


router = routers.DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'circuit-types', CircuitTypeViewSet)
router.register(r'circuits', CircuitViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Providers
    url(r'^providers/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_PROVIDER},
        name='provider_graphs'),

]
