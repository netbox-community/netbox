from dcim.models import Interface
from netbox.views import generic
from utilities.tables import paginate_table
from utilities.utils import count_related
from . import filtersets, forms, tables
from .models import *


#
# Wireless LAN groups
#

class WirelessLANGroupListView(generic.ObjectListView):
    queryset = WirelessLANGroup.objects.add_related_count(
        WirelessLANGroup.objects.all(),
        WirelessLAN,
        'group',
        'wirelesslan_count',
        cumulative=True
    )
    filterset = filtersets.WirelessLANGroupFilterSet
    filterset_form = forms.WirelessLANGroupFilterForm
    table = tables.WirelessLANGroupTable


class WirelessLANGroupView(generic.ObjectView):
    queryset = WirelessLANGroup.objects.all()

    def get_extra_context(self, request, instance):
        wirelesslans = WirelessLAN.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        wirelesslans_table = tables.WirelessLANTable(wirelesslans, exclude=('group',))
        paginate_table(wirelesslans_table, request)

        return {
            'wirelesslans_table': wirelesslans_table,
        }


class WirelessLANGroupEditView(generic.ObjectEditView):
    queryset = WirelessLANGroup.objects.all()
    model_form = forms.WirelessLANGroupForm


class WirelessLANGroupDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLANGroup.objects.all()


class WirelessLANGroupBulkImportView(generic.BulkImportView):
    queryset = WirelessLANGroup.objects.all()
    model_form = forms.WirelessLANGroupCSVForm
    table = tables.WirelessLANGroupTable


class WirelessLANGroupBulkEditView(generic.BulkEditView):
    queryset = WirelessLANGroup.objects.add_related_count(
        WirelessLANGroup.objects.all(),
        WirelessLAN,
        'group',
        'wirelesslan_count',
        cumulative=True
    )
    filterset = filtersets.WirelessLANGroupFilterSet
    table = tables.WirelessLANGroupTable
    form = forms.WirelessLANGroupBulkEditForm


class WirelessLANGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLANGroup.objects.add_related_count(
        WirelessLANGroup.objects.all(),
        WirelessLAN,
        'group',
        'wirelesslan_count',
        cumulative=True
    )
    filterset = filtersets.WirelessLANGroupFilterSet
    table = tables.WirelessLANGroupTable


#
# Wireless LANs
#

class WirelessLANListView(generic.ObjectListView):
    queryset = WirelessLAN.objects.annotate(
        interface_count=count_related(Interface, 'wireless_lans')
    )
    filterset = filtersets.WirelessLANFilterSet
    filterset_form = forms.WirelessLANFilterForm
    table = tables.WirelessLANTable


class WirelessLANView(generic.ObjectView):
    queryset = WirelessLAN.objects.all()

    def get_extra_context(self, request, instance):
        attached_interfaces = Interface.objects.restrict(request.user, 'view').filter(
            wireless_lans=instance
        )
        interfaces_table = tables.WirelessLANInterfacesTable(attached_interfaces)
        paginate_table(interfaces_table, request)

        return {
            'interfaces_table': interfaces_table,
        }


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


#
# Wireless Links
#

class WirelessLinkListView(generic.ObjectListView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    filterset_form = forms.WirelessLinkFilterForm
    table = tables.WirelessLinkTable


class WirelessLinkView(generic.ObjectView):
    queryset = WirelessLink.objects.all()


class WirelessLinkEditView(generic.ObjectEditView):
    queryset = WirelessLink.objects.all()
    model_form = forms.WirelessLinkForm


class WirelessLinkDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLink.objects.all()


class WirelessLinkBulkImportView(generic.BulkImportView):
    queryset = WirelessLink.objects.all()
    model_form = forms.WirelessLinkCSVForm
    table = tables.WirelessLinkTable


class WirelessLinkBulkEditView(generic.BulkEditView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
    form = forms.WirelessLinkBulkEditForm


class WirelessLinkBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
