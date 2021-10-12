from netbox.views import generic
from . import filtersets, forms, tables
from .models import *


#
# SSIDs
#

class SSIDListView(generic.ObjectListView):
    queryset = SSID.objects.all()
    filterset = filtersets.SSIDFilterSet
    filterset_form = forms.SSIDFilterForm
    table = tables.SSIDTable


class SSIDView(generic.ObjectView):
    queryset = SSID.objects.prefetch_related('power_panel', 'rack')


class SSIDEditView(generic.ObjectEditView):
    queryset = SSID.objects.all()
    model_form = forms.SSIDForm


class SSIDDeleteView(generic.ObjectDeleteView):
    queryset = SSID.objects.all()


class SSIDBulkImportView(generic.BulkImportView):
    queryset = SSID.objects.all()
    model_form = forms.SSIDCSVForm
    table = tables.SSIDTable


class SSIDBulkEditView(generic.BulkEditView):
    queryset = SSID.objects.prefetch_related('power_panel', 'rack')
    filterset = filtersets.SSIDFilterSet
    table = tables.SSIDTable
    form = forms.SSIDBulkEditForm


class SSIDBulkDeleteView(generic.BulkDeleteView):
    queryset = SSID.objects.prefetch_related('power_panel', 'rack')
    filterset = filtersets.SSIDFilterSet
    table = tables.SSIDTable
