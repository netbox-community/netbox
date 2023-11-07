from netbox.views import generic
from utilities.utils import count_related
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import *


#
# Tunnels
#

class TunnelListView(generic.ObjectListView):
    queryset = Tunnel.objects.annotate(
        count_terminations=count_related(TunnelTermination, 'tunnel')
    )
    filterset = filtersets.TunnelFilterSet
    filterset_form = forms.TunnelFilterForm
    table = tables.TunnelTable


@register_model_view(Tunnel)
class TunnelView(generic.ObjectView):
    queryset = Tunnel.objects.all()


@register_model_view(Tunnel, 'edit')
class TunnelEditView(generic.ObjectEditView):
    queryset = Tunnel.objects.all()
    form = forms.TunnelForm


@register_model_view(Tunnel, 'delete')
class TunnelDeleteView(generic.ObjectDeleteView):
    queryset = Tunnel.objects.all()


class TunnelBulkImportView(generic.BulkImportView):
    queryset = Tunnel.objects.all()
    model_form = forms.TunnelImportForm


class TunnelBulkEditView(generic.BulkEditView):
    queryset = Tunnel.objects.annotate(
        count_terminations=count_related(TunnelTermination, 'tunnel')
    )
    filterset = filtersets.TunnelFilterSet
    table = tables.TunnelTable
    form = forms.TunnelBulkEditForm


class TunnelBulkDeleteView(generic.BulkDeleteView):
    queryset = Tunnel.objects.annotate(
        count_terminations=count_related(TunnelTermination, 'tunnel')
    )
    filterset = filtersets.TunnelFilterSet
    table = tables.TunnelTable


#
# Tunnel terminations
#

class TunnelTerminationListView(generic.ObjectListView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    filterset_form = forms.TunnelTerminationFilterForm
    table = tables.TunnelTerminationTable


@register_model_view(TunnelTermination)
class TunnelTerminationView(generic.ObjectView):
    queryset = TunnelTermination.objects.all()


@register_model_view(TunnelTermination, 'edit')
class TunnelTerminationEditView(generic.ObjectEditView):
    queryset = TunnelTermination.objects.all()
    form = forms.TunnelTerminationForm


@register_model_view(TunnelTermination, 'delete')
class TunnelTerminationDeleteView(generic.ObjectDeleteView):
    queryset = TunnelTermination.objects.all()


class TunnelTerminationBulkImportView(generic.BulkImportView):
    queryset = TunnelTermination.objects.all()
    model_form = forms.TunnelTerminationImportForm


class TunnelTerminationBulkEditView(generic.BulkEditView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    table = tables.TunnelTerminationTable
    form = forms.TunnelTerminationBulkEditForm


class TunnelTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    table = tables.TunnelTerminationTable


#
# IPSec profiles
#

class IPSecProfileListView(generic.ObjectListView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    filterset_form = forms.IPSecProfileFilterForm
    table = tables.IPSecProfileTable


@register_model_view(IPSecProfile)
class IPSecProfileView(generic.ObjectView):
    queryset = IPSecProfile.objects.all()


@register_model_view(IPSecProfile, 'edit')
class IPSecProfileEditView(generic.ObjectEditView):
    queryset = IPSecProfile.objects.all()
    form = forms.IPSecProfileForm


@register_model_view(IPSecProfile, 'delete')
class IPSecProfileDeleteView(generic.ObjectDeleteView):
    queryset = IPSecProfile.objects.all()


class IPSecProfileBulkImportView(generic.BulkImportView):
    queryset = IPSecProfile.objects.all()
    model_form = forms.IPSecProfileImportForm


class IPSecProfileBulkEditView(generic.BulkEditView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    table = tables.IPSecProfileTable
    form = forms.IPSecProfileBulkEditForm


class IPSecProfileBulkDeleteView(generic.BulkDeleteView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    table = tables.IPSecProfileTable
