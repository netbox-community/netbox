from django.urls import reverse

from circuits.models import (
    Circuit,
    CircuitGroupAssignment,
    CircuitTermination,
    ProviderAccount,
    ProviderNetwork,
    VirtualCircuit,
    VirtualCircuitTermination,
)
from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs


@register_breadcrumbs
class ProviderAccountBreadcrumbs(BreadcrumbTrail):
    model = ProviderAccount
    items = (
        Breadcrumb('provider', url=lambda o: f"{reverse('circuits:provideraccount_list')}?provider_id={o.pk}"),
    )


@register_breadcrumbs
class ProviderNetworkBreadcrumbs(BreadcrumbTrail):
    model = ProviderNetwork
    items = (
        Breadcrumb('provider', url=lambda o: f"{reverse('circuits:providernetwork_list')}?provider_id={o.pk}"),
    )


@register_breadcrumbs
class CircuitBreadcrumbs(BreadcrumbTrail):
    model = Circuit
    items = (
        Breadcrumb('provider', url=lambda o: f"{reverse('circuits:circuit_list')}?provider_id={o.pk}"),
    )


@register_breadcrumbs
class CircuitTerminationBreadcrumbs(BreadcrumbTrail):
    model = CircuitTermination
    items = (
        Breadcrumb('circuit.provider', url=lambda o: f"{reverse('circuits:circuit_list')}?provider_id={o.pk}"),
    )


@register_breadcrumbs
class CircuitGroupAssignmentBreadcrumbs(BreadcrumbTrail):
    model = CircuitGroupAssignment
    items = (
        Breadcrumb('group', url=lambda o: f"{reverse('circuits:circuitgroupassignment_list')}?group_id={o.pk}"),
    )


@register_breadcrumbs
class VirtualCircuitBreadcrumbs(BreadcrumbTrail):
    model = VirtualCircuit
    items = (
        Breadcrumb('provider', url=lambda o: f"{reverse('circuits:virtualcircuit_list')}?provider_id={o.pk}"),
        Breadcrumb(
            'provider_network',
            url=lambda o: f"{reverse('circuits:virtualcircuit_list')}?provider_network_id={o.pk}",
        ),
    )


@register_breadcrumbs
class VirtualCircuitTerminationBreadcrumbs(BreadcrumbTrail):
    model = VirtualCircuitTermination
    items = (
        Breadcrumb(
            'virtual_circuit.provider',
            url=lambda o: f"{reverse('circuits:virtualcircuit_list')}?provider_id={o.pk}",
        ),
        Breadcrumb(
            'virtual_circuit.provider_network',
            url=lambda o: f"{reverse('circuits:virtualcircuit_list')}?provider_network_id={o.pk}",
        ),
        Breadcrumb(
            'virtual_circuit',
            url=lambda o: f"{reverse('circuits:virtualcircuittermination_list')}?virtual_circuit_id={o.pk}",
        ),
    )
