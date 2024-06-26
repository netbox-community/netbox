from dcim.models import Interface
from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin, register_model_view
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
    ).prefetch_related('tags')
    filterset = filtersets.WirelessLANGroupFilterSet
    filterset_form = forms.WirelessLANGroupFilterForm
    table = tables.WirelessLANGroupTable


@register_model_view(WirelessLANGroup)
class WirelessLANGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = WirelessLANGroup.objects.all()

    def get_extra_context(self, request, instance):
        groups = instance.get_descendants(include_self=True)

        return {
            'related_models': self.get_related_models(request, groups),
        }


@register_model_view(WirelessLANGroup, 'edit')
class WirelessLANGroupEditView(generic.ObjectEditView):
    queryset = WirelessLANGroup.objects.all()
    form = forms.WirelessLANGroupForm


@register_model_view(WirelessLANGroup, 'delete')
class WirelessLANGroupDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLANGroup.objects.all()


class WirelessLANGroupBulkImportView(generic.BulkImportView):
    queryset = WirelessLANGroup.objects.all()
    model_form = forms.WirelessLANGroupImportForm


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


@register_model_view(WirelessLAN)
class WirelessLANView(generic.ObjectView):
    queryset = WirelessLAN.objects.all()

    def get_extra_context(self, request, instance):
        attached_interfaces = Interface.objects.restrict(request.user, 'view').filter(
            wireless_lans=instance
        )
        interfaces_table = tables.WirelessLANInterfacesTable(attached_interfaces, user=request.user)
        interfaces_table.configure(request)

        return {
            'interfaces_table': interfaces_table,
        }


@register_model_view(WirelessLAN, 'edit')
class WirelessLANEditView(generic.ObjectEditView):
    queryset = WirelessLAN.objects.all()
    form = forms.WirelessLANForm


@register_model_view(WirelessLAN, 'delete')
class WirelessLANDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLAN.objects.all()


class WirelessLANBulkImportView(generic.BulkImportView):
    queryset = WirelessLAN.objects.all()
    model_form = forms.WirelessLANImportForm


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


@register_model_view(WirelessLink)
class WirelessLinkView(generic.ObjectView):
    queryset = WirelessLink.objects.all()


@register_model_view(WirelessLink, 'edit')
class WirelessLinkEditView(generic.ObjectEditView):
    queryset = WirelessLink.objects.all()
    form = forms.WirelessLinkForm


@register_model_view(WirelessLink, 'delete')
class WirelessLinkDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLink.objects.all()


class WirelessLinkBulkImportView(generic.BulkImportView):
    queryset = WirelessLink.objects.all()
    model_form = forms.WirelessLinkImportForm


class WirelessLinkBulkEditView(generic.BulkEditView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
    form = forms.WirelessLinkBulkEditForm


class WirelessLinkBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
