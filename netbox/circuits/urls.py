from __future__ import unicode_literals

from django.conf.urls import url

from extras.views import ObjectChangeLogView
from . import views
from .models import Circuit, CircuitType, Provider

app_name = 'circuits'
urlpatterns = [

    # Providers
    url(r'^providers/$', views.ProviderListView.as_view(), name='provider_list'),
    url(r'^providers/add/$', views.ProviderCreateView.as_view(), name='provider_add'),
    url(r'^providers/import/$', views.ProviderBulkImportView.as_view(), name='provider_import'),
    url(r'^providers/edit/$', views.ProviderBulkEditView.as_view(), name='provider_bulk_edit'),
    url(r'^providers/delete/$', views.ProviderBulkDeleteView.as_view(), name='provider_bulk_delete'),
    url(r'^providers/(?P<slug>[\w-]+)/$', views.ProviderView.as_view(), name='provider'),
    url(r'^providers/(?P<slug>[\w-]+)/edit/$', views.ProviderEditView.as_view(), name='provider_edit'),
    url(r'^providers/(?P<slug>[\w-]+)/delete/$', views.ProviderDeleteView.as_view(), name='provider_delete'),
    url(r'^providers/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='provider_changelog', kwargs={'model': Provider}),

    # Circuit types
    url(r'^circuit-types/$', views.CircuitTypeListView.as_view(), name='circuittype_list'),
    url(r'^circuit-types/add/$', views.CircuitTypeCreateView.as_view(), name='circuittype_add'),
    url(r'^circuit-types/import/$', views.CircuitTypeBulkImportView.as_view(), name='circuittype_import'),
    url(r'^circuit-types/delete/$', views.CircuitTypeBulkDeleteView.as_view(), name='circuittype_bulk_delete'),
    url(r'^circuit-types/(?P<slug>[\w-]+)/edit/$', views.CircuitTypeEditView.as_view(), name='circuittype_edit'),
    url(r'^circuit-types/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='circuittype_changelog', kwargs={'model': CircuitType}),

    # Circuits
    url(r'^circuits/$', views.CircuitListView.as_view(), name='circuit_list'),
    url(r'^circuits/add/$', views.CircuitCreateView.as_view(), name='circuit_add'),
    url(r'^circuits/import/$', views.CircuitBulkImportView.as_view(), name='circuit_import'),
    url(r'^circuits/edit/$', views.CircuitBulkEditView.as_view(), name='circuit_bulk_edit'),
    url(r'^circuits/delete/$', views.CircuitBulkDeleteView.as_view(), name='circuit_bulk_delete'),
    url(r'^circuits/(?P<pk>\d+)/$', views.CircuitView.as_view(), name='circuit'),
    url(r'^circuits/(?P<pk>\d+)/edit/$', views.CircuitEditView.as_view(), name='circuit_edit'),
    url(r'^circuits/(?P<pk>\d+)/delete/$', views.CircuitDeleteView.as_view(), name='circuit_delete'),
    url(r'^circuits/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='circuit_changelog', kwargs={'model': Circuit}),
    url(r'^circuits/(?P<pk>\d+)/terminations/swap/$', views.circuit_terminations_swap, name='circuit_terminations_swap'),

    # Circuit terminations
    url(r'^circuits/(?P<circuit>\d+)/terminations/add/$', views.CircuitTerminationCreateView.as_view(), name='circuittermination_add'),
    url(r'^circuit-terminations/(?P<pk>\d+)/edit/$', views.CircuitTerminationEditView.as_view(), name='circuittermination_edit'),
    url(r'^circuit-terminations/(?P<pk>\d+)/delete/$', views.CircuitTerminationDeleteView.as_view(), name='circuittermination_delete'),

]
