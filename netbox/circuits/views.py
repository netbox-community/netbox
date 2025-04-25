from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from dcim.views import PathTraceView
from ipam.models import ASN
from netbox.views import generic
from tenancy.views import ObjectContactsView
from utilities.forms import ConfirmationForm
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin, register_model_view
from . import filtersets, forms, tables
from .models import *


#
# Providers
#

@register_model_view(Provider, 'list', path='', detail=False)
class ProviderListView(generic.ObjectListView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider'),
        asn_count=count_related(ASN, 'providers'),
        account_count=count_related(ProviderAccount, 'provider'),
    )
    filterset = filtersets.ProviderFilterSet
    filterset_form = forms.ProviderFilterForm
    table = tables.ProviderTable


@register_model_view(Provider)
class ProviderView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Provider.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(
                request,
                instance,
                omit=(),
                extra=(
                    (
                        VirtualCircuit.objects.restrict(request.user, 'view').filter(
                            provider_network__provider=instance
                        ),
                        'provider_id',
                    ),
                ),
                ),
        }


@register_model_view(Provider, 'add', detail=False)
@register_model_view(Provider, 'edit')
class ProviderEditView(generic.ObjectEditView):
    queryset = Provider.objects.all()
    form = forms.ProviderForm


@register_model_view(Provider, 'delete')
class ProviderDeleteView(generic.ObjectDeleteView):
    queryset = Provider.objects.all()


@register_model_view(Provider, 'bulk_import', path='import', detail=False)
class ProviderBulkImportView(generic.BulkImportView):
    queryset = Provider.objects.all()
    model_form = forms.ProviderImportForm


@register_model_view(Provider, 'bulk_edit', path='edit', detail=False)
class ProviderBulkEditView(generic.BulkEditView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet
    table = tables.ProviderTable
    form = forms.ProviderBulkEditForm


@register_model_view(Provider, 'bulk_delete', path='delete', detail=False)
class ProviderBulkDeleteView(generic.BulkDeleteView):
    queryset = Provider.objects.annotate(
        count_circuits=count_related(Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet
    table = tables.ProviderTable


@register_model_view(Provider, 'contacts')
class ProviderContactsView(ObjectContactsView):
    queryset = Provider.objects.all()


#
# ProviderAccounts
#

@register_model_view(ProviderAccount, 'list', path='', detail=False)
class ProviderAccountListView(generic.ObjectListView):
    queryset = ProviderAccount.objects.annotate(
        count_circuits=count_related(Circuit, 'provider_account')
    )
    filterset = filtersets.ProviderAccountFilterSet
    filterset_form = forms.ProviderAccountFilterForm
    table = tables.ProviderAccountTable


@register_model_view(ProviderAccount)
class ProviderAccountView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ProviderAccount.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(ProviderAccount, 'add', detail=False)
@register_model_view(ProviderAccount, 'edit')
class ProviderAccountEditView(generic.ObjectEditView):
    queryset = ProviderAccount.objects.all()
    form = forms.ProviderAccountForm


@register_model_view(ProviderAccount, 'delete')
class ProviderAccountDeleteView(generic.ObjectDeleteView):
    queryset = ProviderAccount.objects.all()


@register_model_view(ProviderAccount, 'bulk_import', path='import', detail=False)
class ProviderAccountBulkImportView(generic.BulkImportView):
    queryset = ProviderAccount.objects.all()
    model_form = forms.ProviderAccountImportForm
    table = tables.ProviderAccountTable


@register_model_view(ProviderAccount, 'bulk_edit', path='edit', detail=False)
class ProviderAccountBulkEditView(generic.BulkEditView):
    queryset = ProviderAccount.objects.annotate(
        count_circuits=count_related(Circuit, 'provider_account')
    )
    filterset = filtersets.ProviderAccountFilterSet
    table = tables.ProviderAccountTable
    form = forms.ProviderAccountBulkEditForm


@register_model_view(ProviderAccount, 'bulk_delete', path='delete', detail=False)
class ProviderAccountBulkDeleteView(generic.BulkDeleteView):
    queryset = ProviderAccount.objects.annotate(
        count_circuits=count_related(Circuit, 'provider_account')
    )
    filterset = filtersets.ProviderAccountFilterSet
    table = tables.ProviderAccountTable


@register_model_view(ProviderAccount, 'contacts')
class ProviderAccountContactsView(ObjectContactsView):
    queryset = ProviderAccount.objects.all()


#
# Provider networks
#

@register_model_view(ProviderNetwork, 'list', path='', detail=False)
class ProviderNetworkListView(generic.ObjectListView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    filterset_form = forms.ProviderNetworkFilterForm
    table = tables.ProviderNetworkTable


@register_model_view(ProviderNetwork)
class ProviderNetworkView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ProviderNetwork.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(
                request,
                instance,
                omit=(CircuitTermination,),
                extra=(
                    (
                        Circuit.objects.restrict(request.user, 'view').filter(terminations___provider_network=instance),
                        'provider_network_id',
                    ),
                    (
                        CircuitTermination.objects.restrict(request.user, 'view').filter(_provider_network=instance),
                        'provider_network_id',
                    ),
                ),
            ),
        }


@register_model_view(ProviderNetwork, 'add', detail=False)
@register_model_view(ProviderNetwork, 'edit')
class ProviderNetworkEditView(generic.ObjectEditView):
    queryset = ProviderNetwork.objects.all()
    form = forms.ProviderNetworkForm


@register_model_view(ProviderNetwork, 'delete')
class ProviderNetworkDeleteView(generic.ObjectDeleteView):
    queryset = ProviderNetwork.objects.all()


@register_model_view(ProviderNetwork, 'bulk_import', path='import', detail=False)
class ProviderNetworkBulkImportView(generic.BulkImportView):
    queryset = ProviderNetwork.objects.all()
    model_form = forms.ProviderNetworkImportForm


@register_model_view(ProviderNetwork, 'bulk_edit', path='edit', detail=False)
class ProviderNetworkBulkEditView(generic.BulkEditView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    table = tables.ProviderNetworkTable
    form = forms.ProviderNetworkBulkEditForm


@register_model_view(ProviderNetwork, 'bulk_delete', path='delete', detail=False)
class ProviderNetworkBulkDeleteView(generic.BulkDeleteView):
    queryset = ProviderNetwork.objects.all()
    filterset = filtersets.ProviderNetworkFilterSet
    table = tables.ProviderNetworkTable


#
# Circuit Types
#

@register_model_view(CircuitType, 'list', path='', detail=False)
class CircuitTypeListView(generic.ObjectListView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.CircuitTypeFilterSet
    filterset_form = forms.CircuitTypeFilterForm
    table = tables.CircuitTypeTable


@register_model_view(CircuitType)
class CircuitTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = CircuitType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(CircuitType, 'add', detail=False)
@register_model_view(CircuitType, 'edit')
class CircuitTypeEditView(generic.ObjectEditView):
    queryset = CircuitType.objects.all()
    form = forms.CircuitTypeForm


@register_model_view(CircuitType, 'delete')
class CircuitTypeDeleteView(generic.ObjectDeleteView):
    queryset = CircuitType.objects.all()


@register_model_view(CircuitType, 'bulk_import', path='import', detail=False)
class CircuitTypeBulkImportView(generic.BulkImportView):
    queryset = CircuitType.objects.all()
    model_form = forms.CircuitTypeImportForm


@register_model_view(CircuitType, 'bulk_edit', path='edit', detail=False)
class CircuitTypeBulkEditView(generic.BulkEditView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.CircuitTypeFilterSet
    table = tables.CircuitTypeTable
    form = forms.CircuitTypeBulkEditForm


@register_model_view(CircuitType, 'bulk_delete', path='delete', detail=False)
class CircuitTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = CircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.CircuitTypeFilterSet
    table = tables.CircuitTypeTable


#
# Circuits
#

@register_model_view(Circuit, 'list', path='', detail=False)
class CircuitListView(generic.ObjectListView):
    queryset = Circuit.objects.prefetch_related(
        'tenant__group', 'termination_a__termination', 'termination_z__termination',
    )
    filterset = filtersets.CircuitFilterSet
    filterset_form = forms.CircuitFilterForm
    table = tables.CircuitTable


@register_model_view(Circuit)
class CircuitView(generic.ObjectView):
    queryset = Circuit.objects.all()


@register_model_view(Circuit, 'add', detail=False)
@register_model_view(Circuit, 'edit')
class CircuitEditView(generic.ObjectEditView):
    queryset = Circuit.objects.all()
    form = forms.CircuitForm


@register_model_view(Circuit, 'delete')
class CircuitDeleteView(generic.ObjectDeleteView):
    queryset = Circuit.objects.all()


@register_model_view(Circuit, 'bulk_import', path='import', detail=False)
class CircuitBulkImportView(generic.BulkImportView):
    queryset = Circuit.objects.all()
    model_form = forms.CircuitImportForm
    additional_permissions = [
        'circuits.add_circuittermination',
    ]
    related_object_forms = {
        'terminations': forms.CircuitTerminationImportRelatedForm,
    }

    def prep_related_object_data(self, parent, data):
        data.update({'circuit': parent})
        return data


@register_model_view(Circuit, 'bulk_edit', path='edit', detail=False)
class CircuitBulkEditView(generic.BulkEditView):
    queryset = Circuit.objects.prefetch_related(
        'tenant__group', 'termination_a__termination', 'termination_z__termination',
    )
    filterset = filtersets.CircuitFilterSet
    table = tables.CircuitTable
    form = forms.CircuitBulkEditForm


@register_model_view(Circuit, 'bulk_delete', path='delete', detail=False)
class CircuitBulkDeleteView(generic.BulkDeleteView):
    queryset = Circuit.objects.prefetch_related(
        'tenant__group', 'termination_a__termination', 'termination_z__termination',
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
            messages.error(request, _(
                "No terminations have been defined for circuit {circuit}."
            ).format(circuit=circuit))
            return redirect('circuits:circuit', pk=circuit.pk)

        return render(request, 'circuits/circuit_terminations_swap.html', {
            'circuit': circuit,
            'termination_a': circuit.termination_a,
            'termination_z': circuit.termination_z,
            'form': form,
            'panel_class': 'light',
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
                    circuit.refresh_from_db()
                    circuit.termination_a = termination_z
                    circuit.termination_z = termination_a
                    circuit.save()
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

            messages.success(request, _("Swapped terminations for circuit {circuit}.").format(circuit=circuit))
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


@register_model_view(Circuit, 'contacts')
class CircuitContactsView(ObjectContactsView):
    queryset = Circuit.objects.all()


#
# Circuit terminations
#

@register_model_view(CircuitTermination, 'list', path='', detail=False)
class CircuitTerminationListView(generic.ObjectListView):
    queryset = CircuitTermination.objects.all()
    filterset = filtersets.CircuitTerminationFilterSet
    filterset_form = forms.CircuitTerminationFilterForm
    table = tables.CircuitTerminationTable


@register_model_view(CircuitTermination)
class CircuitTerminationView(generic.ObjectView):
    queryset = CircuitTermination.objects.all()


@register_model_view(CircuitTermination, 'add', detail=False)
@register_model_view(CircuitTermination, 'edit')
class CircuitTerminationEditView(generic.ObjectEditView):
    queryset = CircuitTermination.objects.all()
    form = forms.CircuitTerminationForm


@register_model_view(CircuitTermination, 'delete')
class CircuitTerminationDeleteView(generic.ObjectDeleteView):
    queryset = CircuitTermination.objects.all()


@register_model_view(CircuitTermination, 'bulk_import', path='import', detail=False)
class CircuitTerminationBulkImportView(generic.BulkImportView):
    queryset = CircuitTermination.objects.all()
    model_form = forms.CircuitTerminationImportForm


@register_model_view(CircuitTermination, 'bulk_edit', path='edit', detail=False)
class CircuitTerminationBulkEditView(generic.BulkEditView):
    queryset = CircuitTermination.objects.all()
    filterset = filtersets.CircuitTerminationFilterSet
    table = tables.CircuitTerminationTable
    form = forms.CircuitTerminationBulkEditForm


@register_model_view(CircuitTermination, 'bulk_delete', path='delete', detail=False)
class CircuitTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = CircuitTermination.objects.all()
    filterset = filtersets.CircuitTerminationFilterSet
    table = tables.CircuitTerminationTable


# Trace view
register_model_view(CircuitTermination, 'trace', kwargs={'model': CircuitTermination})(PathTraceView)


#
# Circuit Groups
#

@register_model_view(CircuitGroup, 'list', path='', detail=False)
class CircuitGroupListView(generic.ObjectListView):
    queryset = CircuitGroup.objects.annotate(
        circuit_group_assignment_count=count_related(CircuitGroupAssignment, 'group')
    )
    filterset = filtersets.CircuitGroupFilterSet
    filterset_form = forms.CircuitGroupFilterForm
    table = tables.CircuitGroupTable


@register_model_view(CircuitGroup)
class CircuitGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = CircuitGroup.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(CircuitGroup, 'add', detail=False)
@register_model_view(CircuitGroup, 'edit')
class CircuitGroupEditView(generic.ObjectEditView):
    queryset = CircuitGroup.objects.all()
    form = forms.CircuitGroupForm


@register_model_view(CircuitGroup, 'delete')
class CircuitGroupDeleteView(generic.ObjectDeleteView):
    queryset = CircuitGroup.objects.all()


@register_model_view(CircuitGroup, 'bulk_import', path='import', detail=False)
class CircuitGroupBulkImportView(generic.BulkImportView):
    queryset = CircuitGroup.objects.all()
    model_form = forms.CircuitGroupImportForm


@register_model_view(CircuitGroup, 'bulk_edit', path='edit', detail=False)
class CircuitGroupBulkEditView(generic.BulkEditView):
    queryset = CircuitGroup.objects.all()
    filterset = filtersets.CircuitGroupFilterSet
    table = tables.CircuitGroupTable
    form = forms.CircuitGroupBulkEditForm


@register_model_view(CircuitGroup, 'bulk_delete', path='delete', detail=False)
class CircuitGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = CircuitGroup.objects.all()
    filterset = filtersets.CircuitGroupFilterSet
    table = tables.CircuitGroupTable


#
# Circuit Groups
#

@register_model_view(CircuitGroupAssignment, 'list', path='', detail=False)
class CircuitGroupAssignmentListView(generic.ObjectListView):
    queryset = CircuitGroupAssignment.objects.all()
    filterset = filtersets.CircuitGroupAssignmentFilterSet
    filterset_form = forms.CircuitGroupAssignmentFilterForm
    table = tables.CircuitGroupAssignmentTable


@register_model_view(CircuitGroupAssignment)
class CircuitGroupAssignmentView(generic.ObjectView):
    queryset = CircuitGroupAssignment.objects.all()


@register_model_view(CircuitGroupAssignment, 'add', detail=False)
@register_model_view(CircuitGroupAssignment, 'edit')
class CircuitGroupAssignmentEditView(generic.ObjectEditView):
    queryset = CircuitGroupAssignment.objects.all()
    form = forms.CircuitGroupAssignmentForm


@register_model_view(CircuitGroupAssignment, 'delete')
class CircuitGroupAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = CircuitGroupAssignment.objects.all()


@register_model_view(CircuitGroupAssignment, 'bulk_import', path='import', detail=False)
class CircuitGroupAssignmentBulkImportView(generic.BulkImportView):
    queryset = CircuitGroupAssignment.objects.all()
    model_form = forms.CircuitGroupAssignmentImportForm


@register_model_view(CircuitGroupAssignment, 'bulk_edit', path='edit', detail=False)
class CircuitGroupAssignmentBulkEditView(generic.BulkEditView):
    queryset = CircuitGroupAssignment.objects.all()
    filterset = filtersets.CircuitGroupAssignmentFilterSet
    table = tables.CircuitGroupAssignmentTable
    form = forms.CircuitGroupAssignmentBulkEditForm


@register_model_view(CircuitGroupAssignment, 'bulk_delete', path='delete', detail=False)
class CircuitGroupAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = CircuitGroupAssignment.objects.all()
    filterset = filtersets.CircuitGroupAssignmentFilterSet
    table = tables.CircuitGroupAssignmentTable


#
# Virtual circuit Types
#

@register_model_view(VirtualCircuitType, 'list', path='', detail=False)
class VirtualCircuitTypeListView(generic.ObjectListView):
    queryset = VirtualCircuitType.objects.annotate(
        virtual_circuit_count=count_related(VirtualCircuit, 'type')
    )
    filterset = filtersets.VirtualCircuitTypeFilterSet
    filterset_form = forms.VirtualCircuitTypeFilterForm
    table = tables.VirtualCircuitTypeTable


@register_model_view(VirtualCircuitType)
class VirtualCircuitTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = VirtualCircuitType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(VirtualCircuitType, 'add', detail=False)
@register_model_view(VirtualCircuitType, 'edit')
class VirtualCircuitTypeEditView(generic.ObjectEditView):
    queryset = VirtualCircuitType.objects.all()
    form = forms.VirtualCircuitTypeForm


@register_model_view(VirtualCircuitType, 'delete')
class VirtualCircuitTypeDeleteView(generic.ObjectDeleteView):
    queryset = VirtualCircuitType.objects.all()


@register_model_view(VirtualCircuitType, 'bulk_import', path='import', detail=False)
class VirtualCircuitTypeBulkImportView(generic.BulkImportView):
    queryset = VirtualCircuitType.objects.all()
    model_form = forms.VirtualCircuitTypeImportForm


@register_model_view(VirtualCircuitType, 'bulk_edit', path='edit', detail=False)
class VirtualCircuitTypeBulkEditView(generic.BulkEditView):
    queryset = VirtualCircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.VirtualCircuitTypeFilterSet
    table = tables.VirtualCircuitTypeTable
    form = forms.VirtualCircuitTypeBulkEditForm


@register_model_view(VirtualCircuitType, 'bulk_delete', path='delete', detail=False)
class VirtualCircuitTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualCircuitType.objects.annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    filterset = filtersets.VirtualCircuitTypeFilterSet
    table = tables.VirtualCircuitTypeTable


#
# Virtual circuits
#

class VirtualCircuitListView(generic.ObjectListView):
    queryset = VirtualCircuit.objects.annotate(
        termination_count=count_related(VirtualCircuitTermination, 'virtual_circuit')
    )
    filterset = filtersets.VirtualCircuitFilterSet
    filterset_form = forms.VirtualCircuitFilterForm
    table = tables.VirtualCircuitTable


@register_model_view(VirtualCircuit)
class VirtualCircuitView(generic.ObjectView):
    queryset = VirtualCircuit.objects.all()


@register_model_view(VirtualCircuit, 'edit')
class VirtualCircuitEditView(generic.ObjectEditView):
    queryset = VirtualCircuit.objects.all()
    form = forms.VirtualCircuitForm


@register_model_view(VirtualCircuit, 'delete')
class VirtualCircuitDeleteView(generic.ObjectDeleteView):
    queryset = VirtualCircuit.objects.all()


class VirtualCircuitBulkImportView(generic.BulkImportView):
    queryset = VirtualCircuit.objects.all()
    model_form = forms.VirtualCircuitImportForm
    additional_permissions = [
        'circuits.add_virtualcircuittermination',
    ]
    related_object_forms = {
        'terminations': forms.VirtualCircuitTerminationImportRelatedForm,
    }

    def prep_related_object_data(self, parent, data):
        data.update({'virtual_circuit': parent})
        return data


class VirtualCircuitBulkEditView(generic.BulkEditView):
    queryset = VirtualCircuit.objects.annotate(
        termination_count=count_related(VirtualCircuitTermination, 'virtual_circuit')
    )
    filterset = filtersets.VirtualCircuitFilterSet
    table = tables.VirtualCircuitTable
    form = forms.VirtualCircuitBulkEditForm


class VirtualCircuitBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualCircuit.objects.annotate(
        termination_count=count_related(VirtualCircuitTermination, 'virtual_circuit')
    )
    filterset = filtersets.VirtualCircuitFilterSet
    table = tables.VirtualCircuitTable


#
# Virtual circuit terminations
#

class VirtualCircuitTerminationListView(generic.ObjectListView):
    queryset = VirtualCircuitTermination.objects.all()
    filterset = filtersets.VirtualCircuitTerminationFilterSet
    filterset_form = forms.VirtualCircuitTerminationFilterForm
    table = tables.VirtualCircuitTerminationTable


@register_model_view(VirtualCircuitTermination)
class VirtualCircuitTerminationView(generic.ObjectView):
    queryset = VirtualCircuitTermination.objects.all()


@register_model_view(VirtualCircuitTermination, 'edit')
class VirtualCircuitTerminationEditView(generic.ObjectEditView):
    queryset = VirtualCircuitTermination.objects.all()
    form = forms.VirtualCircuitTerminationForm


@register_model_view(VirtualCircuitTermination, 'delete')
class VirtualCircuitTerminationDeleteView(generic.ObjectDeleteView):
    queryset = VirtualCircuitTermination.objects.all()


class VirtualCircuitTerminationBulkImportView(generic.BulkImportView):
    queryset = VirtualCircuitTermination.objects.all()
    model_form = forms.VirtualCircuitTerminationImportForm


class VirtualCircuitTerminationBulkEditView(generic.BulkEditView):
    queryset = VirtualCircuitTermination.objects.all()
    filterset = filtersets.VirtualCircuitTerminationFilterSet
    table = tables.VirtualCircuitTerminationTable
    form = forms.VirtualCircuitTerminationBulkEditForm


class VirtualCircuitTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualCircuitTermination.objects.all()
    filterset = filtersets.VirtualCircuitTerminationFilterSet
    table = tables.VirtualCircuitTerminationTable
