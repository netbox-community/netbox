from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)

from . import filters, forms, tables
from .models import Circuit, CircuitType, Provider


#
# Providers
#

class ProviderListView(ObjectListView):
    queryset = Provider.objects.annotate(count_circuits=Count('circuits'))
    filter = filters.ProviderFilter
    filter_form = forms.ProviderFilterForm
    table = tables.ProviderTable
    edit_permissions = ['circuits.change_provider', 'circuits.delete_provider']
    template_name = 'circuits/provider_list.html'


def provider(request, slug):

    provider = get_object_or_404(Provider, slug=slug)
    circuits = Circuit.objects.filter(provider=provider).select_related('site', 'interface__device')

    return render(request, 'circuits/provider.html', {
        'provider': provider,
        'circuits': circuits,
    })


class ProviderEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.change_provider'
    model = Provider
    form_class = forms.ProviderForm
    template_name = 'circuits/provider_edit.html'
    cancel_url = 'circuits:provider_list'


class ProviderDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'circuits.delete_provider'
    model = Provider
    redirect_url = 'circuits:provider_list'


class ProviderBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'circuits.add_provider'
    form = forms.ProviderImportForm
    table = tables.ProviderTable
    template_name = 'circuits/provider_import.html'
    obj_list_url = 'circuits:provider_list'


class ProviderBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'circuits.change_provider'
    cls = Provider
    form = forms.ProviderBulkEditForm
    template_name = 'circuits/provider_bulk_edit.html'
    default_redirect_url = 'circuits:provider_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        for field in ['asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class ProviderBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_provider'
    cls = Provider
    default_redirect_url = 'circuits:provider_list'


#
# Circuit Types
#

class CircuitTypeListView(ObjectListView):
    queryset = CircuitType.objects.annotate(circuit_count=Count('circuits'))
    table = tables.CircuitTypeTable
    edit_permissions = ['circuits.change_circuittype', 'circuits.delete_circuittype']
    template_name = 'circuits/circuittype_list.html'


class CircuitTypeEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.change_circuittype'
    model = CircuitType
    form_class = forms.CircuitTypeForm
    success_url = 'circuits:circuittype_list'
    cancel_url = 'circuits:circuittype_list'


class CircuitTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuittype'
    cls = CircuitType
    default_redirect_url = 'circuits:circuittype_list'


#
# Circuits
#

class CircuitListView(ObjectListView):
    queryset = Circuit.objects.select_related('provider', 'type', 'tenant', 'site')
    filter = filters.CircuitFilter
    filter_form = forms.CircuitFilterForm
    table = tables.CircuitTable
    edit_permissions = ['circuits.change_circuit', 'circuits.delete_circuit']
    template_name = 'circuits/circuit_list.html'


def circuit(request, pk):

    circuit = get_object_or_404(Circuit, pk=pk)

    return render(request, 'circuits/circuit.html', {
        'circuit': circuit,
    })


class CircuitEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'circuits.change_circuit'
    model = Circuit
    form_class = forms.CircuitForm
    fields_initial = ['site']
    template_name = 'circuits/circuit_edit.html'
    cancel_url = 'circuits:circuit_list'


class CircuitDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'circuits.delete_circuit'
    model = Circuit
    redirect_url = 'circuits:circuit_list'


class CircuitBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'circuits.add_circuit'
    form = forms.CircuitImportForm
    table = tables.CircuitTable
    template_name = 'circuits/circuit_import.html'
    obj_list_url = 'circuits:circuit_list'


class CircuitBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'circuits.change_circuit'
    cls = Circuit
    form = forms.CircuitBulkEditForm
    template_name = 'circuits/circuit_bulk_edit.html'
    default_redirect_url = 'circuits:circuit_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        for field in ['type', 'provider', 'port_speed', 'commit_rate', 'comments']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class CircuitBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuit'
    cls = Circuit
    default_redirect_url = 'circuits:circuit_list'
