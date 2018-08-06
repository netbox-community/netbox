from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from extras.models import Graph, GRAPH_TYPE_PROVIDER
from utilities.forms import ConfirmationForm
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .constants import TERM_SIDE_A, TERM_SIDE_Z
from .models import Circuit, CircuitTermination, CircuitType, Provider


#
# Providers
#

class ProviderListView(ObjectListView):
    queryset = Provider.objects.annotate(count_circuits=Count('circuits'))
    filter = filters.ProviderFilter
    filter_form = forms.ProviderFilterForm
    table = tables.ProviderDetailTable
    template_name = 'circuits/provider_list.html'


class ProviderView(View):

    def get(self, request, slug):

        provider = get_object_or_404(Provider, slug=slug)
        circuits = Circuit.objects.filter(provider=provider).select_related(
            'type', 'tenant'
        ).prefetch_related(
            'terminations__site'
        )
        show_graphs = Graph.objects.filter(type=GRAPH_TYPE_PROVIDER).exists()

        return render(request, 'circuits/provider.html', {
            'provider': provider,
            'circuits': circuits,
            'show_graphs': show_graphs,
        })


class ProviderCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.add_provider'
    model = Provider
    model_form = forms.ProviderForm
    template_name = 'circuits/provider_edit.html'
    default_return_url = 'circuits:provider_list'


class ProviderEditView(ProviderCreateView):
    permission_required = 'circuits.change_provider'


class ProviderDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'circuits.delete_provider'
    model = Provider
    default_return_url = 'circuits:provider_list'


class ProviderBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'circuits.add_provider'
    model_form = forms.ProviderCSVForm
    table = tables.ProviderTable
    default_return_url = 'circuits:provider_list'


class ProviderBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'circuits.change_provider'
    queryset = Provider.objects.all()
    filter = filters.ProviderFilter
    table = tables.ProviderTable
    form = forms.ProviderBulkEditForm
    default_return_url = 'circuits:provider_list'


class ProviderBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_provider'
    queryset = Provider.objects.all()
    filter = filters.ProviderFilter
    table = tables.ProviderTable
    default_return_url = 'circuits:provider_list'


#
# Circuit Types
#

class CircuitTypeListView(ObjectListView):
    queryset = CircuitType.objects.annotate(circuit_count=Count('circuits'))
    table = tables.CircuitTypeTable
    template_name = 'circuits/circuittype_list.html'


class CircuitTypeCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.add_circuittype'
    model = CircuitType
    model_form = forms.CircuitTypeForm
    default_return_url = 'circuits:circuittype_list'


class CircuitTypeEditView(CircuitTypeCreateView):
    permission_required = 'circuits.change_circuittype'


class CircuitTypeBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'circuits.add_circuittype'
    model_form = forms.CircuitTypeCSVForm
    table = tables.CircuitTypeTable
    default_return_url = 'circuits:circuittype_list'


class CircuitTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuittype'
    queryset = CircuitType.objects.annotate(circuit_count=Count('circuits'))
    table = tables.CircuitTypeTable
    default_return_url = 'circuits:circuittype_list'


#
# Circuits
#

class CircuitListView(ObjectListView):
    queryset = Circuit.objects.select_related(
        'provider', 'type', 'tenant'
    ).prefetch_related(
        'terminations__site', 'terminations__interface__device'
    )
    filter = filters.CircuitFilter
    filter_form = forms.CircuitFilterForm
    table = tables.CircuitTable
    template_name = 'circuits/circuit_list.html'


class CircuitView(View):

    def get(self, request, pk):

        circuit = get_object_or_404(Circuit.objects.select_related('provider', 'type', 'tenant__group'), pk=pk)
        termination_a = CircuitTermination.objects.select_related(
            'site__region', 'interface__device'
        ).filter(
            circuit=circuit, term_side=TERM_SIDE_A
        ).first()
        termination_z = CircuitTermination.objects.select_related(
            'site__region', 'interface__device'
        ).filter(
            circuit=circuit, term_side=TERM_SIDE_Z
        ).first()

        return render(request, 'circuits/circuit.html', {
            'circuit': circuit,
            'termination_a': termination_a,
            'termination_z': termination_z,
        })


class CircuitCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.add_circuit'
    model = Circuit
    model_form = forms.CircuitForm
    template_name = 'circuits/circuit_edit.html'
    default_return_url = 'circuits:circuit_list'


class CircuitEditView(CircuitCreateView):
    permission_required = 'circuits.change_circuit'


class CircuitDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'circuits.delete_circuit'
    model = Circuit
    default_return_url = 'circuits:circuit_list'


class CircuitBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'circuits.add_circuit'
    model_form = forms.CircuitCSVForm
    table = tables.CircuitTable
    default_return_url = 'circuits:circuit_list'


class CircuitBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'circuits.change_circuit'
    queryset = Circuit.objects.select_related('provider', 'type', 'tenant').prefetch_related('terminations__site')
    filter = filters.CircuitFilter
    table = tables.CircuitTable
    form = forms.CircuitBulkEditForm
    default_return_url = 'circuits:circuit_list'


class CircuitBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuit'
    queryset = Circuit.objects.select_related('provider', 'type', 'tenant').prefetch_related('terminations__site')
    filter = filters.CircuitFilter
    table = tables.CircuitTable
    default_return_url = 'circuits:circuit_list'


@permission_required('circuits.change_circuittermination')
def circuit_terminations_swap(request, pk):

    circuit = get_object_or_404(Circuit, pk=pk)
    termination_a = CircuitTermination.objects.filter(circuit=circuit, term_side=TERM_SIDE_A).first()
    termination_z = CircuitTermination.objects.filter(circuit=circuit, term_side=TERM_SIDE_Z).first()
    if not termination_a and not termination_z:
        messages.error(request, "No terminations have been defined for circuit {}.".format(circuit))
        return redirect('circuits:circuit', pk=circuit.pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            if termination_a and termination_z:
                # Use a placeholder to avoid an IntegrityError on the (circuit, term_side) unique constraint
                with transaction.atomic():
                    termination_a.term_side = '_'
                    termination_a.save()
                    termination_z.term_side = 'A'
                    termination_z.save()
                    termination_a.term_side = 'Z'
                    termination_a.save()
            elif termination_a:
                termination_a.term_side = 'Z'
                termination_a.save()
            else:
                termination_z.term_side = 'A'
                termination_z.save()
            messages.success(request, "Swapped terminations for circuit {}.".format(circuit))
            return redirect('circuits:circuit', pk=circuit.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'circuits/circuit_terminations_swap.html', {
        'circuit': circuit,
        'termination_a': termination_a,
        'termination_z': termination_z,
        'form': form,
        'panel_class': 'default',
        'button_class': 'primary',
        'return_url': circuit.get_absolute_url(),
    })


#
# Circuit terminations
#

class CircuitTerminationCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.add_circuittermination'
    model = CircuitTermination
    model_form = forms.CircuitTerminationForm
    template_name = 'circuits/circuittermination_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'circuit' in url_kwargs:
            obj.circuit = get_object_or_404(Circuit, pk=url_kwargs['circuit'])
        return obj

    def get_return_url(self, request, obj):
        return obj.circuit.get_absolute_url()


class CircuitTerminationEditView(CircuitTerminationCreateView):
    permission_required = 'circuits.change_circuittermination'


class CircuitTerminationDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'circuits.delete_circuittermination'
    model = CircuitTermination
