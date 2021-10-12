from netbox.views import generic
from . import filtersets, forms, tables
from .models import *


#
# Wireless LANs
#

class WirelessLANListView(generic.ObjectListView):
    queryset = WirelessLAN.objects.all()
    filterset = filtersets.WirelessLANFilterSet
    filterset_form = forms.WirelessLANFilterForm
    table = tables.WirelessLANTable


class WirelessLANView(generic.ObjectView):
    queryset = WirelessLAN.objects.all()


class WirelessLANEditView(generic.ObjectEditView):
    queryset = WirelessLAN.objects.all()
    model_form = forms.WirelessLANForm


class WirelessLANDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLAN.objects.all()


class WirelessLANBulkImportView(generic.BulkImportView):
    queryset = WirelessLAN.objects.all()
    model_form = forms.WirelessLANCSVForm
    table = tables.WirelessLANTable


class WirelessLANBulkEditView(generic.BulkEditView):
    queryset = WirelessLAN.objects.all()
    filterset = filtersets.WirelessLANFilterSet
    table = tables.WirelessLANTable
    form = forms.WirelessLANBulkEditForm


class WirelessLANBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLAN.objects.all()
    filterset = filtersets.WirelessLANFilterSet
    table = tables.WirelessLANTable
