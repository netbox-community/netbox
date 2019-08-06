from django.urls import path

from dcim.views import CableCreateView, CableTraceView
from extras.views import ObjectChangeLogView
from . import views
from .models import Circuit, CircuitTermination, CircuitType, Provider

app_name = 'circuits'
urlpatterns = [

    # Providers
    path(r'providers/', views.ProviderListView.as_view(), name='provider_list'),
    path(r'providers/add/', views.ProviderCreateView.as_view(), name='provider_add'),
    path(r'providers/import/', views.ProviderBulkImportView.as_view(), name='provider_import'),
    path(r'providers/edit/', views.ProviderBulkEditView.as_view(), name='provider_bulk_edit'),
    path(r'providers/delete/', views.ProviderBulkDeleteView.as_view(), name='provider_bulk_delete'),
    path(r'providers/<slug:slug>/', views.ProviderView.as_view(), name='provider'),
    path(r'providers/<slug:slug>/edit/', views.ProviderEditView.as_view(), name='provider_edit'),
    path(r'providers/<slug:slug>/delete/', views.ProviderDeleteView.as_view(), name='provider_delete'),
    path(r'providers/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='provider_changelog', kwargs={'model': Provider}),

    # Circuit types
    path(r'circuit-types/', views.CircuitTypeListView.as_view(), name='circuittype_list'),
    path(r'circuit-types/add/', views.CircuitTypeCreateView.as_view(), name='circuittype_add'),
    path(r'circuit-types/import/', views.CircuitTypeBulkImportView.as_view(), name='circuittype_import'),
    path(r'circuit-types/delete/', views.CircuitTypeBulkDeleteView.as_view(), name='circuittype_bulk_delete'),
    path(r'circuit-types/<slug:slug>/edit/', views.CircuitTypeEditView.as_view(), name='circuittype_edit'),
    path(r'circuit-types/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='circuittype_changelog', kwargs={'model': CircuitType}),

    # Circuits
    path(r'circuits/', views.CircuitListView.as_view(), name='circuit_list'),
    path(r'circuits/add/', views.CircuitCreateView.as_view(), name='circuit_add'),
    path(r'circuits/import/', views.CircuitBulkImportView.as_view(), name='circuit_import'),
    path(r'circuits/edit/', views.CircuitBulkEditView.as_view(), name='circuit_bulk_edit'),
    path(r'circuits/delete/', views.CircuitBulkDeleteView.as_view(), name='circuit_bulk_delete'),
    path(r'circuits/<int:pk>/', views.CircuitView.as_view(), name='circuit'),
    path(r'circuits/<int:pk>/edit/', views.CircuitEditView.as_view(), name='circuit_edit'),
    path(r'circuits/<int:pk>/delete/', views.CircuitDeleteView.as_view(), name='circuit_delete'),
    path(r'circuits/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='circuit_changelog', kwargs={'model': Circuit}),
    path(r'circuits/<int:pk>/terminations/swap/', views.circuit_terminations_swap, name='circuit_terminations_swap'),

    # Circuit terminations

    path(r'circuits/<int:circuit>/terminations/add/', views.CircuitTerminationCreateView.as_view(), name='circuittermination_add'),
    path(r'circuit-terminations/<int:pk>/edit/', views.CircuitTerminationEditView.as_view(), name='circuittermination_edit'),
    path(r'circuit-terminations/<int:pk>/delete/', views.CircuitTerminationDeleteView.as_view(), name='circuittermination_delete'),
    path(r'circuit-terminations/<int:termination_a_id>/connect/<str:termination_b_type>/', CableCreateView.as_view(), name='circuittermination_connect', kwargs={'termination_a_type': CircuitTermination}),
    path(r'circuit-terminations/<int:pk>/trace/', CableTraceView.as_view(), name='circuittermination_trace', kwargs={'model': CircuitTermination}),

]
