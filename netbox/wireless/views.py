from dcim.models import Interface
from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin, register_model_view
from . import filtersets, forms, tables
from .models import *


#
# Wireless LAN groups
#

@register_model_view(WirelessLANGroup, 'list', path='', detail=False)
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


@register_model_view(WirelessLANGroup, 'add', detail=False)
@register_model_view(WirelessLANGroup, 'edit')
class WirelessLANGroupEditView(generic.ObjectEditView):
    queryset = WirelessLANGroup.objects.all()
    form = forms.WirelessLANGroupForm


@register_model_view(WirelessLANGroup, 'delete')
class WirelessLANGroupDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLANGroup.objects.all()


@register_model_view(WirelessLANGroup, 'bulk_import', path='import', detail=False)
class WirelessLANGroupBulkImportView(generic.BulkImportView):
    queryset = WirelessLANGroup.objects.all()
    model_form = forms.WirelessLANGroupImportForm


@register_model_view(WirelessLANGroup, 'bulk_edit', path='edit', detail=False)
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


@register_model_view(WirelessLANGroup, 'bulk_delete', path='delete', detail=False)
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

@register_model_view(WirelessLAN, 'list', path='', detail=False)
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


@register_model_view(WirelessLAN, 'add', detail=False)
@register_model_view(WirelessLAN, 'edit')
class WirelessLANEditView(generic.ObjectEditView):
    queryset = WirelessLAN.objects.all()
    form = forms.WirelessLANForm


@register_model_view(WirelessLAN, 'delete')
class WirelessLANDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLAN.objects.all()


@register_model_view(WirelessLAN, 'bulk_import', path='import', detail=False)
class WirelessLANBulkImportView(generic.BulkImportView):
    queryset = WirelessLAN.objects.all()
    model_form = forms.WirelessLANImportForm


@register_model_view(WirelessLAN, 'bulk_edit', path='edit', detail=False)
class WirelessLANBulkEditView(generic.BulkEditView):
    queryset = WirelessLAN.objects.all()
    filterset = filtersets.WirelessLANFilterSet
    table = tables.WirelessLANTable
    form = forms.WirelessLANBulkEditForm


@register_model_view(WirelessLAN, 'bulk_delete', path='delete', detail=False)
class WirelessLANBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLAN.objects.all()
    filterset = filtersets.WirelessLANFilterSet
    table = tables.WirelessLANTable


#
# Wireless Links
#

@register_model_view(WirelessLink, 'list', path='', detail=False)
class WirelessLinkListView(generic.ObjectListView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    filterset_form = forms.WirelessLinkFilterForm
    table = tables.WirelessLinkTable


@register_model_view(WirelessLink)
class WirelessLinkView(generic.ObjectView):
    queryset = WirelessLink.objects.all()


@register_model_view(WirelessLink, 'add', detail=False)
@register_model_view(WirelessLink, 'edit')
class WirelessLinkEditView(generic.ObjectEditView):
    queryset = WirelessLink.objects.all()
    form = forms.WirelessLinkForm


@register_model_view(WirelessLink, 'delete')
class WirelessLinkDeleteView(generic.ObjectDeleteView):
    queryset = WirelessLink.objects.all()


@register_model_view(WirelessLink, 'bulk_import', path='import', detail=False)
class WirelessLinkBulkImportView(generic.BulkImportView):
    queryset = WirelessLink.objects.all()
    model_form = forms.WirelessLinkImportForm


@register_model_view(WirelessLink, 'bulk_edit', path='edit', detail=False)
class WirelessLinkBulkEditView(generic.BulkEditView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
    form = forms.WirelessLinkBulkEditForm


@register_model_view(WirelessLink, 'bulk_delete', path='delete', detail=False)
class WirelessLinkBulkDeleteView(generic.BulkDeleteView):
    queryset = WirelessLink.objects.all()
    filterset = filtersets.WirelessLinkFilterSet
    table = tables.WirelessLinkTable
