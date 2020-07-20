from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import RequestConfig

from extras.models import Graph
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .choices import CircuitTerminationSideChoices
from .models import Circuit, CircuitTermination, CircuitType, Provider


#
# Providers
#

class ProviderListView(ObjectListView):
    queryset = Provider.objects.annotate(count_circuits=Count('circuits')).order_by(*Provider._meta.ordering)
    filterset = filters.ProviderFilterSet
    filterset_form = forms.ProviderFilterForm
    table = tables.ProviderTable


class ProviderView(ObjectView):
    queryset = Provider.objects.all()

    def get(self, request, slug):

        provider = get_object_or_404(self.queryset, slug=slug)
        circuits = Circuit.objects.restrict(request.user, 'view').filter(
            provider=provider
        ).prefetch_related(
            'type', 'tenant', 'terminations__site'
        ).annotate_sites()
        show_graphs = Graph.objects.filter(type__model='provider').exists()

        circuits_table = tables.CircuitTable(circuits)
        circuits_table.columns.hide('provider')

        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(circuits_table)

        return render(request, 'circuits/provider.html', {
            'provider': provider,
            'circuits_table': circuits_table,
            'show_graphs': show_graphs,
        })


class ProviderEditView(ObjectEditView):
    queryset = Provider.objects.all()
    model_form = forms.ProviderForm
    template_name = 'circuits/provider_edit.html'


class ProviderDeleteView(ObjectDeleteView):
    queryset = Provider.objects.all()


class ProviderBulkImportView(BulkImportView):
    queryset = Provider.objects.all()
    model_form = forms.ProviderCSVForm
    table = tables.ProviderTable


class ProviderBulkEditView(BulkEditView):
    queryset = Provider.objects.annotate(count_circuits=Count('circuits')).order_by(*Provider._meta.ordering)
    filterset = filters.ProviderFilterSet
    table = tables.ProviderTable
    form = forms.ProviderBulkEditForm


class ProviderBulkDeleteView(BulkDeleteView):
    queryset = Provider.objects.annotate(count_circuits=Count('circuits')).order_by(*Provider._meta.ordering)
    filterset = filters.ProviderFilterSet
    table = tables.ProviderTable


#
# Circuit Types
#

class CircuitTypeListView(ObjectListView):
    queryset = CircuitType.objects.annotate(circuit_count=Count('circuits')).order_by(*CircuitType._meta.ordering)
    table = tables.CircuitTypeTable


class CircuitTypeEditView(ObjectEditView):
    queryset = CircuitType.objects.all()
    model_form = forms.CircuitTypeForm


class CircuitTypeDeleteView(ObjectDeleteView):
    queryset = CircuitType.objects.all()


class CircuitTypeBulkImportView(BulkImportView):
    queryset = CircuitType.objects.all()
    model_form = forms.CircuitTypeCSVForm
    table = tables.CircuitTypeTable


class CircuitTypeBulkDeleteView(BulkDeleteView):
    queryset = CircuitType.objects.annotate(circuit_count=Count('circuits')).order_by(*CircuitType._meta.ordering)
    table = tables.CircuitTypeTable


#
# Circuits
#

class CircuitListView(ObjectListView):
    queryset = Circuit.objects.prefetch_related(
        Prefetch('terminations', CircuitTermination.objects.unrestricted()),
        'provider', 'type', 'tenant'
    ).annotate_sites()
    filterset = filters.CircuitFilterSet
    filterset_form = forms.CircuitFilterForm
    table = tables.CircuitTable


class CircuitView(ObjectView):
    queryset = Circuit.objects.prefetch_related('provider', 'type', 'tenant__group')

    def get(self, request, pk):
        circuit = get_object_or_404(self.queryset, pk=pk)

        termination_a = CircuitTermination.objects.restrict(request.user, 'view').prefetch_related(
            'site__region', 'connected_endpoint__device'
        ).filter(
            circuit=circuit, term_side=CircuitTerminationSideChoices.SIDE_A
        ).first()
        if termination_a and termination_a.connected_endpoint:
            termination_a.ip_addresses = termination_a.connected_endpoint.ip_addresses.restrict(request.user, 'view')

        termination_z = CircuitTermination.objects.restrict(request.user, 'view').prefetch_related(
            'site__region', 'connected_endpoint__device'
        ).filter(
            circuit=circuit, term_side=CircuitTerminationSideChoices.SIDE_Z
        ).first()
        if termination_z and termination_z.connected_endpoint:
            termination_z.ip_addresses = termination_z.connected_endpoint.ip_addresses.restrict(request.user, 'view')

        return render(request, 'circuits/circuit.html', {
            'circuit': circuit,
            'termination_a': termination_a,
            'termination_z': termination_z,
        })


class CircuitEditView(ObjectEditView):
    queryset = Circuit.objects.all()
    model_form = forms.CircuitForm
    template_name = 'circuits/circuit_edit.html'


class CircuitDeleteView(ObjectDeleteView):
    queryset = Circuit.objects.all()


class CircuitBulkImportView(BulkImportView):
    queryset = Circuit.objects.all()
    model_form = forms.CircuitCSVForm
    table = tables.CircuitTable


class CircuitBulkEditView(BulkEditView):
    queryset = Circuit.objects.prefetch_related(
        Prefetch('terminations', CircuitTermination.objects.unrestricted()),
        'provider', 'type', 'tenant'
    )
    filterset = filters.CircuitFilterSet
    table = tables.CircuitTable
    form = forms.CircuitBulkEditForm


class CircuitBulkDeleteView(BulkDeleteView):
    queryset = Circuit.objects.prefetch_related(
        Prefetch('terminations', CircuitTermination.objects.unrestricted()),
        'provider', 'type', 'tenant'
    )
    filterset = filters.CircuitFilterSet
    table = tables.CircuitTable


class CircuitSwapTerminations(ObjectEditView):
    """
    Swap the A and Z terminations of a circuit.
    """
    queryset = Circuit.objects.all()

    def get(self, request, pk):
        circuit = get_object_or_404(self.queryset, pk=pk)
        form = ConfirmationForm()

        # Circuit must have at least one termination to swap
        if not circuit.termination_a and not circuit.termination_z:
            messages.error(request, "No terminations have been defined for circuit {}.".format(circuit))
            return redirect('circuits:circuit', pk=circuit.pk)

        return render(request, 'circuits/circuit_terminations_swap.html', {
            'circuit': circuit,
            'termination_a': circuit.termination_a,
            'termination_z': circuit.termination_z,
            'form': form,
            'panel_class': 'default',
            'button_class': 'primary',
            'return_url': circuit.get_absolute_url(),
        })

    def post(self, request, pk):
        circuit = get_object_or_404(self.queryset, pk=pk)
        form = ConfirmationForm(request.POST)

        if form.is_valid():

            termination_a = CircuitTermination.objects.filter(
                circuit=circuit, term_side=CircuitTerminationSideChoices.SIDE_A
            ).first()
            termination_z = CircuitTermination.objects.filter(
                circuit=circuit, term_side=CircuitTerminationSideChoices.SIDE_Z
            ).first()

            if termination_a and termination_z:
                # Use a placeholder to avoid an IntegrityError on the (circuit, term_side) unique constraint
                print('swapping')
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

        return render(request, 'circuits/circuit_terminations_swap.html', {
            'circuit': circuit,
            'termination_a': circuit.termination_a,
            'termination_z': circuit.termination_z,
            'form': form,
            'panel_class': 'default',
            'button_class': 'primary',
            'return_url': circuit.get_absolute_url(),
        })


#
# Circuit terminations
#

class CircuitTerminationEditView(ObjectEditView):
    queryset = CircuitTermination.objects.all()
    model_form = forms.CircuitTerminationForm
    template_name = 'circuits/circuittermination_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'circuit' in url_kwargs:
            obj.circuit = get_object_or_404(Circuit, pk=url_kwargs['circuit'])
        return obj

    def get_return_url(self, request, obj):
        return obj.circuit.get_absolute_url()


class CircuitTerminationDeleteView(ObjectDeleteView):
    queryset = CircuitTermination.objects.all()
