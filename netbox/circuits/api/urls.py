from django.conf.urls import url

from extras.models import GRAPH_TYPE_PROVIDER
from extras.api.views import GraphListView

from .views import *


urlpatterns = [

    # Providers
    url(r'^providers/$', ProviderViewSet.as_view({'get': 'list'}), name='provider_list'),
    url(r'^providers/(?P<pk>\d+)/$', ProviderViewSet.as_view({'get': 'retrieve'}), name='provider_detail'),
    url(r'^providers/(?P<pk>\d+)/graphs/$', GraphListView.as_view(), {'type': GRAPH_TYPE_PROVIDER},
        name='provider_graphs'),

    # Circuit types
    url(r'^circuit-types/$', CircuitTypeViewSet.as_view({'get': 'list'}), name='circuittype_list'),
    url(r'^circuit-types/(?P<pk>\d+)/$', CircuitTypeViewSet.as_view({'get': 'retrieve'}), name='circuittype_detail'),

    # Circuits
    url(r'^circuits/$', CircuitViewSet.as_view({'get': 'list'}), name='circuit_list'),
    url(r'^circuits/(?P<pk>\d+)/$', CircuitViewSet.as_view({'get': 'retrieve'}), name='circuit_detail'),

]
