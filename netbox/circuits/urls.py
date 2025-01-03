from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'circuits'
urlpatterns = [
    path('providers/', include(get_model_urls('circuits', 'provider', detail=False))),
    path('providers/<int:pk>/', include(get_model_urls('circuits', 'provider'))),

    path('provider-accounts/', include(get_model_urls('circuits', 'provideraccount', detail=False))),
    path('provider-accounts/<int:pk>/', include(get_model_urls('circuits', 'provideraccount'))),

    path('provider-networks/', include(get_model_urls('circuits', 'providernetwork', detail=False))),
    path('provider-networks/<int:pk>/', include(get_model_urls('circuits', 'providernetwork'))),

    path('circuit-types/', include(get_model_urls('circuits', 'circuittype', detail=False))),
    path('circuit-types/<int:pk>/', include(get_model_urls('circuits', 'circuittype'))),

    path('circuits/', include(get_model_urls('circuits', 'circuit', detail=False))),
    path(
        'circuits/<int:pk>/terminations/swap/',
        views.CircuitSwapTerminations.as_view(),
        name='circuit_terminations_swap'
    ),
    path('circuits/<int:pk>/', include(get_model_urls('circuits', 'circuit'))),

    path('circuit-terminations/', include(get_model_urls('circuits', 'circuittermination', detail=False))),
    path('circuit-terminations/<int:pk>/', include(get_model_urls('circuits', 'circuittermination'))),

    path('circuit-groups/', include(get_model_urls('circuits', 'circuitgroup', detail=False))),
    path('circuit-groups/<int:pk>/', include(get_model_urls('circuits', 'circuitgroup'))),

    path('circuit-group-assignments/', include(get_model_urls('circuits', 'circuitgroupassignment', detail=False))),
    path('circuit-group-assignments/<int:pk>/', include(get_model_urls('circuits', 'circuitgroupassignment'))),

    # Virtual circuits
    path('virtual-circuits/', views.VirtualCircuitListView.as_view(), name='virtualcircuit_list'),
    path('virtual-circuits/add/', views.VirtualCircuitEditView.as_view(), name='virtualcircuit_add'),
    path('virtual-circuits/import/', views.VirtualCircuitBulkImportView.as_view(), name='virtualcircuit_bulk_import'),
    path('virtual-circuits/edit/', views.VirtualCircuitBulkEditView.as_view(), name='virtualcircuit_bulk_edit'),
    path('virtual-circuits/delete/', views.VirtualCircuitBulkDeleteView.as_view(), name='virtualcircuit_bulk_delete'),
    path('virtual-circuits/<int:pk>/', include(get_model_urls('circuits', 'virtualcircuit'))),

    path('virtual-circuit-types/', include(get_model_urls('circuits', 'virtualcircuittype', detail=False))),
    path('virtual-circuit-types/<int:pk>/', include(get_model_urls('circuits', 'virtualcircuittype'))),

    # Virtual circuit terminations
    path(
        'virtual-circuit-terminations/',
        views.VirtualCircuitTerminationListView.as_view(),
        name='virtualcircuittermination_list',
    ),
    path(
        'virtual-circuit-terminations/add/',
        views.VirtualCircuitTerminationEditView.as_view(),
        name='virtualcircuittermination_add',
    ),
    path(
        'virtual-circuit-terminations/import/',
        views.VirtualCircuitTerminationBulkImportView.as_view(),
        name='virtualcircuittermination_bulk_import',
    ),
    path(
        'virtual-circuit-terminations/edit/',
        views.VirtualCircuitTerminationBulkEditView.as_view(),
        name='virtualcircuittermination_bulk_edit',
    ),
    path(
        'virtual-circuit-terminations/delete/',
        views.VirtualCircuitTerminationBulkDeleteView.as_view(),
        name='virtualcircuittermination_bulk_delete',
    ),
    path('virtual-circuit-terminations/<int:pk>/', include(get_model_urls('circuits', 'virtualcircuittermination'))),
]
