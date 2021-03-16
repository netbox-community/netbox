from django.urls import path

from dcim.views import CableCreateView, PathTraceView
from extras.views import ObjectChangeLogView
from . import views
from .models import Circuit, CircuitTermination, CircuitType, Provider

app_name = 'circuits'
urlpatterns = [

    # Providers
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/add/', views.ProviderEditView.as_view(), name='provider_add'),
    path('providers/import/', views.ProviderBulkImportView.as_view(), name='provider_import'),
    path('providers/edit/', views.ProviderBulkEditView.as_view(), name='provider_bulk_edit'),
    path('providers/delete/', views.ProviderBulkDeleteView.as_view(), name='provider_bulk_delete'),
    path('providers/<slug:slug>/', views.ProviderView.as_view(), name='provider'),
    path('providers/<slug:slug>/edit/', views.ProviderEditView.as_view(), name='provider_edit'),
    path('providers/<slug:slug>/delete/', views.ProviderDeleteView.as_view(), name='provider_delete'),
    path('providers/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='provider_changelog', kwargs={'model': Provider}),

    # Circuit types
    path('circuit-types/', views.CircuitTypeListView.as_view(), name='circuittype_list'),
    path('circuit-types/add/', views.CircuitTypeEditView.as_view(), name='circuittype_add'),
    path('circuit-types/import/', views.CircuitTypeBulkImportView.as_view(), name='circuittype_import'),
    path('circuit-types/delete/', views.CircuitTypeBulkDeleteView.as_view(), name='circuittype_bulk_delete'),
    path('circuit-types/<slug:slug>/edit/', views.CircuitTypeEditView.as_view(), name='circuittype_edit'),
    path('circuit-types/<slug:slug>/delete/', views.CircuitTypeDeleteView.as_view(), name='circuittype_delete'),
    path('circuit-types/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='circuittype_changelog', kwargs={'model': CircuitType}),

    # Circuits
    path('circuits/', views.CircuitListView.as_view(), name='circuit_list'),
    path('circuits/add/', views.CircuitEditView.as_view(), name='circuit_add'),
    path('circuits/import/', views.CircuitBulkImportView.as_view(), name='circuit_import'),
    path('circuits/edit/', views.CircuitBulkEditView.as_view(), name='circuit_bulk_edit'),
    path('circuits/delete/', views.CircuitBulkDeleteView.as_view(), name='circuit_bulk_delete'),
    path('circuits/<int:pk>/', views.CircuitView.as_view(), name='circuit'),
    path('circuits/<int:pk>/edit/', views.CircuitEditView.as_view(), name='circuit_edit'),
    path('circuits/<int:pk>/delete/', views.CircuitDeleteView.as_view(), name='circuit_delete'),
    path('circuits/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='circuit_changelog', kwargs={'model': Circuit}),
    path('circuits/<int:pk>/terminations/swap/', views.CircuitSwapTerminations.as_view(), name='circuit_terminations_swap'),

    # Circuit terminations
    path('circuits/<int:circuit>/terminations/add/', views.CircuitTerminationEditView.as_view(), name='circuittermination_add'),
    path('circuit-terminations/<int:pk>/edit/', views.CircuitTerminationEditView.as_view(), name='circuittermination_edit'),
    path('circuit-terminations/<int:pk>/delete/', views.CircuitTerminationDeleteView.as_view(), name='circuittermination_delete'),
    path('circuit-terminations/<int:termination_a_id>/connect/<str:termination_b_type>/', CableCreateView.as_view(), name='circuittermination_connect', kwargs={'termination_a_type': CircuitTermination}),
    path('circuit-terminations/<int:pk>/trace/', PathTraceView.as_view(), name='circuittermination_trace', kwargs={'model': CircuitTermination}),

]
