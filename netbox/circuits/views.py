from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from netbox.views import generic
from utilities.forms import ConfirmationForm
from utilities.tables import paginate_table
from utilities.utils import count_related
from . import filtersets, forms, tables
from .choices import CircuitTerminationSideChoices
from .models import *


#
# Providers
#

class ProviderListView(generic.ObjectListView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet
    filterset_form = forms.ProviderFilterForm
    table = tables.ProviderTable


class ProviderView(generic.ObjectView):
    queryset = Provider.objects.all()

    def get_extra_context(self, request, instance):
        circuits = Circuit.objects.restrict(request.user, 'view').filter(
            provider=instance
        ).prefetch_related(
            'type', 'tenant', 'terminations__site'
        )

        circuits_table = tables.CircuitTable(circuits)
        circuits_table.columns.hide('provider')
        paginate_table(circuits_table, request)

        return {
            'circuits_table': circuits_table,
        }


class ProviderEditView(generic.ObjectEditView):
    queryset = Provider.objects.all()
    model_form = forms.ProviderForm


class ProviderDeleteView(generic.ObjectDeleteView):
    queryset = Provider.objects.all()


class ProviderBulkImportView(generic.BulkImportView):
    queryset = Provider.objects.all()
    model_form = forms.ProviderCSVForm
    table = tables.ProviderTable


class ProviderBulkEditView(generic.BulkEditView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet
    table = tables.ProviderTable
    form = forms.ProviderBulkEditForm


class ProviderBulkDeleteView(generic.BulkDeleteView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet
    table = tables.ProviderTable


#
# Provider networks
#

class ProviderNetworkListView(generic.ObjectListView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    filterset_form = forms.ProviderNetworkFilterForm
    table = tables.ProviderNetworkTable


class ProviderNetworkView(generic.ObjectView):
    queryset = ProviderNetwork.objects.all()

    def get_extra_context(self, request, instance):
        circuits = Circuit.objects.restrict(request.user, 'view').filter(
            Q(termination_a__provider_network=instance.pk) |
            Q(termination_z__provider_network=instance.pk)
        ).prefetch_related(
            'type', 'tenant', 'terminations__site'
        )

        circuits_table = tables.CircuitTable(circuits)
        circuits_table.columns.hide('termination_a')
        circuits_table.columns.hide('termination_z')
        paginate_table(circuits_table, request)

        return {
            'circuits_table': circuits_table,
        }


class ProviderNetworkEditView(generic.ObjectEditView):
    queryset = ProviderNetwork.objects.all()
    model_form = forms.ProviderNetworkForm


class ProviderNetworkDeleteView(generic.ObjectDeleteView):
    queryset = ProviderNetwork.objects.all()


class ProviderNetworkBulkImportView(generic.BulkImportView):
    queryset = ProviderNetwork.objects.all()
    model_form = forms.ProviderNetworkCSVForm
    table = tables.ProviderNetworkTable


class ProviderNetworkBulkEditView(generic.BulkEditView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    table = tables.ProviderNetworkTable
    form = forms.ProviderNetworkBulkEditForm


class ProviderNetworkBulkDeleteView(generic.BulkDeleteView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    table = tables.ProviderNetworkTable


#
# Circuit Types
#

class CircuitTypeListView(generic.ObjectListView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    table = tables.CircuitTypeTable


class CircuitTypeView(generic.ObjectView):
    queryset = CircuitType.objects.all()

    def get_extra_context(self, request, instance):
        circuits = Circuit.objects.restrict(request.user, 'view').filter(
            type=instance
        )

        circuits_table = tables.CircuitTable(circuits)
        circuits_table.columns.hide('type')
        paginate_table(circuits_table, request)

        return {
            'circuits_table': circuits_table,
        }


class CircuitTypeEditView(generic.ObjectEditView):
    queryset = CircuitType.objects.all()
    model_form = forms.CircuitTypeForm


class CircuitTypeDeleteView(generic.ObjectDeleteView):
    queryset = CircuitType.objects.all()


class CircuitTypeBulkImportView(generic.BulkImportView):
    queryset = CircuitType.objects.all()
    model_form = forms.CircuitTypeCSVForm
    table = tables.CircuitTypeTable


class CircuitTypeBulkEditView(generic.BulkEditView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.CircuitTypeFilterSet
    table = tables.CircuitTypeTable
    form = forms.CircuitTypeBulkEditForm


class CircuitTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    table = tables.CircuitTypeTable


#
# Circuits
#

class CircuitListView(generic.ObjectListView):
    queryset = Circuit.objects.prefetch_related(
        'provider', 'type', 'tenant', 'termination_a', 'termination_z'
    )
    filterset = filtersets.CircuitFilterSet
    filterset_form = forms.CircuitFilterForm
    table = tables.CircuitTable


class CircuitView(generic.ObjectView):
    queryset = Circuit.objects.all()


class CircuitEditView(generic.ObjectEditView):
    queryset = Circuit.objects.all()
    model_form = forms.CircuitForm


class CircuitDeleteView(generic.ObjectDeleteView):
    queryset = Circuit.objects.all()


class CircuitBulkImportView(generic.BulkImportView):
    queryset = Circuit.objects.all()
    model_form = forms.CircuitCSVForm
    table = tables.CircuitTable


class CircuitBulkEditView(generic.BulkEditView):
    queryset = Circuit.objects.prefetch_related(
        'provider', 'type', 'tenant', 'terminations'
    )
    filterset = filtersets.CircuitFilterSet
    table = tables.CircuitTable
    form = forms.CircuitBulkEditForm


class CircuitBulkDeleteView(generic.BulkDeleteView):
    queryset = Circuit.objects.prefetch_related(
        'provider', 'type', 'tenant', 'terminations'
    )
    filterset = filtersets.CircuitFilterSet
    table = tables.CircuitTable


class CircuitSwapTerminations(generic.ObjectEditView):
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

            termination_a = CircuitTermination.objects.filter(pk=circuit.termination_a_id).first()
            termination_z = CircuitTermination.objects.filter(pk=circuit.termination_z_id).first()

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
                circuit.refresh_from_db()
                circuit.termination_a = None
                circuit.save()
            else:
                termination_z.term_side = 'A'
                termination_z.save()
                circuit.refresh_from_db()
                circuit.termination_z = None
                circuit.save()

            print(f'term A: {circuit.termination_a}')
            print(f'term Z: {circuit.termination_z}')

            messages.success(request, f"Swapped terminations for circuit {circuit}.")
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

class CircuitTerminationEditView(generic.ObjectEditView):
    queryset = CircuitTermination.objects.all()
    model_form = forms.CircuitTerminationForm
    template_name = 'circuits/circuittermination_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'circuit' in url_kwargs:
            obj.circuit = get_object_or_404(Circuit, pk=url_kwargs['circuit'])
        return obj

    def get_return_url(self, request, obj):
        return obj.circuit.get_absolute_url()


class CircuitTerminationDeleteView(generic.ObjectDeleteView):
    queryset = CircuitTermination.objects.all()
