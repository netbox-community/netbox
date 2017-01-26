from django.conf.urls import include, url

from rest_framework import routers

from extras.models import GRAPH_TYPE_PROVIDER
from extras.api.views import GraphListView

from . import views


router = routers.DefaultRouter()
router.register(r'providers', views.ProviderViewSet)
router.register(r'circuit-types', views.CircuitTypeViewSet)
router.register(r'circuits', views.CircuitViewSet)
router.register(r'circuit-terminations', views.CircuitTerminationViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

    # Providers
    url(r'^providers/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_PROVIDER},
        name='provider_graphs'),

    # Circuits
    url(r'^circuits/(?P<pk>\d+)/terminations/$', views.NestedCircuitTerminationViewSet.as_view({'get': 'list'})),

]
