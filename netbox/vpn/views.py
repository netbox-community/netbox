from django.utils.translation import gettext_lazy as _

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from ipam.tables import RouteTargetTable
from netbox.object_actions import AddObject, BulkDelete, BulkEdit, BulkExport, BulkImport
from netbox.ui import actions, layout
from netbox.ui.panels import (
    CommentsPanel,
    ContextTablePanel,
    ObjectsTablePanel,
    PluginContentPanel,
    RelatedObjectsPanel,
    TemplatePanel,
)
from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin, register_model_view

from . import filtersets, forms, tables
from .models import *
from .ui import panels

#
# Tunnel groups
#


@register_model_view(TunnelGroup, 'list', path='', detail=False)
class TunnelGroupListView(generic.ObjectListView):
    queryset = TunnelGroup.objects.annotate(
        tunnel_count=count_related(Tunnel, 'group')
    )
    filterset = filtersets.TunnelGroupFilterSet
    filterset_form = forms.TunnelGroupFilterForm
    table = tables.TunnelGroupTable


@register_model_view(TunnelGroup)
class TunnelGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = TunnelGroup.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.TunnelGroupPanel(),
            TagsPanel(),
        ],
        right_panels=[
            RelatedObjectsPanel(),
            CommentsPanel(),
            CustomFieldsPanel(),
        ],
    )

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(TunnelGroup, 'add', detail=False)
@register_model_view(TunnelGroup, 'edit')
class TunnelGroupEditView(generic.ObjectEditView):
    queryset = TunnelGroup.objects.all()
    form = forms.TunnelGroupForm


@register_model_view(TunnelGroup, 'delete')
class TunnelGroupDeleteView(generic.ObjectDeleteView):
    queryset = TunnelGroup.objects.all()


@register_model_view(TunnelGroup, 'bulk_import', path='import', detail=False)
class TunnelGroupBulkImportView(generic.BulkImportView):
    queryset = TunnelGroup.objects.all()
    model_form = forms.TunnelGroupImportForm


@register_model_view(TunnelGroup, 'bulk_edit', path='edit', detail=False)
class TunnelGroupBulkEditView(generic.BulkEditView):
    queryset = TunnelGroup.objects.annotate(
        tunnel_count=count_related(Tunnel, 'group')
    )
    filterset = filtersets.TunnelGroupFilterSet
    table = tables.TunnelGroupTable
    form = forms.TunnelGroupBulkEditForm


@register_model_view(TunnelGroup, 'bulk_rename', path='rename', detail=False)
class TunnelGroupBulkRenameView(generic.BulkRenameView):
    queryset = TunnelGroup.objects.all()
    filterset = filtersets.TunnelGroupFilterSet


@register_model_view(TunnelGroup, 'bulk_delete', path='delete', detail=False)
class TunnelGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = TunnelGroup.objects.annotate(
        tunnel_count=count_related(Tunnel, 'group')
    )
    filterset = filtersets.TunnelGroupFilterSet
    table = tables.TunnelGroupTable


#
# Tunnels
#

@register_model_view(Tunnel, 'list', path='', detail=False)
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
    layout = layout.SimpleLayout(
        left_panels=[
            panels.TunnelPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            TagsPanel(),
            CommentsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.tunneltermination',
                filters={'tunnel_id': lambda ctx: ctx['object'].pk},
                actions=[
                    actions.AddObject(
                        'vpn.tunneltermination',
                        url_params={'tunnel': lambda ctx: ctx['object'].pk},
                        label=_('Add a Termination'),
                    ),
                ],
                title=_('Terminations'),
            ),
        ],
    )


@register_model_view(Tunnel, 'add', detail=False)
@register_model_view(Tunnel, 'edit')
class TunnelEditView(generic.ObjectEditView):
    queryset = Tunnel.objects.all()
    form = forms.TunnelForm

    def dispatch(self, request, *args, **kwargs):

        # If creating a new Tunnel, use the creation form
        if 'pk' not in kwargs:
            self.form = forms.TunnelCreateForm

        return super().dispatch(request, *args, **kwargs)


@register_model_view(Tunnel, 'delete')
class TunnelDeleteView(generic.ObjectDeleteView):
    queryset = Tunnel.objects.all()


@register_model_view(Tunnel, 'bulk_import', path='import', detail=False)
class TunnelBulkImportView(generic.BulkImportView):
    queryset = Tunnel.objects.all()
    model_form = forms.TunnelImportForm


@register_model_view(Tunnel, 'bulk_edit', path='edit', detail=False)
class TunnelBulkEditView(generic.BulkEditView):
    queryset = Tunnel.objects.annotate(
        count_terminations=count_related(TunnelTermination, 'tunnel')
    )
    filterset = filtersets.TunnelFilterSet
    table = tables.TunnelTable
    form = forms.TunnelBulkEditForm


@register_model_view(Tunnel, 'bulk_rename', path='rename', detail=False)
class TunnelBulkRenameView(generic.BulkRenameView):
    queryset = Tunnel.objects.all()
    filterset = filtersets.TunnelFilterSet


@register_model_view(Tunnel, 'bulk_delete', path='delete', detail=False)
class TunnelBulkDeleteView(generic.BulkDeleteView):
    queryset = Tunnel.objects.annotate(
        count_terminations=count_related(TunnelTermination, 'tunnel')
    )
    filterset = filtersets.TunnelFilterSet
    table = tables.TunnelTable


#
# Tunnel terminations
#

@register_model_view(TunnelTermination, 'list', path='', detail=False)
class TunnelTerminationListView(generic.ObjectListView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    filterset_form = forms.TunnelTerminationFilterForm
    table = tables.TunnelTerminationTable


@register_model_view(TunnelTermination)
class TunnelTerminationView(generic.ObjectView):
    queryset = TunnelTermination.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.TunnelTerminationPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            TagsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.tunneltermination',
                filters={
                    'tunnel_id': lambda ctx: ctx['object'].tunnel.pk,
                    'id__n': lambda ctx: ctx['object'].pk,
                },
                title=_('Peer Terminations'),
            ),
        ],
    )


@register_model_view(TunnelTermination, 'add', detail=False)
@register_model_view(TunnelTermination, 'edit')
class TunnelTerminationEditView(generic.ObjectEditView):
    queryset = TunnelTermination.objects.all()
    form = forms.TunnelTerminationForm


@register_model_view(TunnelTermination, 'delete')
class TunnelTerminationDeleteView(generic.ObjectDeleteView):
    queryset = TunnelTermination.objects.all()


@register_model_view(TunnelTermination, 'bulk_import', path='import', detail=False)
class TunnelTerminationBulkImportView(generic.BulkImportView):
    queryset = TunnelTermination.objects.all()
    model_form = forms.TunnelTerminationImportForm


@register_model_view(TunnelTermination, 'bulk_edit', path='edit', detail=False)
class TunnelTerminationBulkEditView(generic.BulkEditView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    table = tables.TunnelTerminationTable
    form = forms.TunnelTerminationBulkEditForm


@register_model_view(TunnelTermination, 'bulk_delete', path='delete', detail=False)
class TunnelTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = TunnelTermination.objects.all()
    filterset = filtersets.TunnelTerminationFilterSet
    table = tables.TunnelTerminationTable


#
# IKE proposals
#

@register_model_view(IKEProposal, 'list', path='', detail=False)
class IKEProposalListView(generic.ObjectListView):
    queryset = IKEProposal.objects.all()
    filterset = filtersets.IKEProposalFilterSet
    filterset_form = forms.IKEProposalFilterForm
    table = tables.IKEProposalTable


@register_model_view(IKEProposal)
class IKEProposalView(generic.ObjectView):
    queryset = IKEProposal.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.IKEProposalPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            CommentsPanel(),
            TagsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.ikepolicy',
                filters={'ike_proposal_id': lambda ctx: ctx['object'].pk},
                title=_('IKE Policies'),
            ),
        ],
    )


@register_model_view(IKEProposal, 'add', detail=False)
@register_model_view(IKEProposal, 'edit')
class IKEProposalEditView(generic.ObjectEditView):
    queryset = IKEProposal.objects.all()
    form = forms.IKEProposalForm


@register_model_view(IKEProposal, 'delete')
class IKEProposalDeleteView(generic.ObjectDeleteView):
    queryset = IKEProposal.objects.all()


@register_model_view(IKEProposal, 'bulk_import', path='import', detail=False)
class IKEProposalBulkImportView(generic.BulkImportView):
    queryset = IKEProposal.objects.all()
    model_form = forms.IKEProposalImportForm


@register_model_view(IKEProposal, 'bulk_edit', path='edit', detail=False)
class IKEProposalBulkEditView(generic.BulkEditView):
    queryset = IKEProposal.objects.all()
    filterset = filtersets.IKEProposalFilterSet
    table = tables.IKEProposalTable
    form = forms.IKEProposalBulkEditForm


@register_model_view(IKEProposal, 'bulk_rename', path='rename', detail=False)
class IKEProposalBulkRenameView(generic.BulkRenameView):
    queryset = IKEProposal.objects.all()
    filterset = filtersets.IKEProposalFilterSet


@register_model_view(IKEProposal, 'bulk_delete', path='delete', detail=False)
class IKEProposalBulkDeleteView(generic.BulkDeleteView):
    queryset = IKEProposal.objects.all()
    filterset = filtersets.IKEProposalFilterSet
    table = tables.IKEProposalTable


#
# IKE policies
#

@register_model_view(IKEPolicy, 'list', path='', detail=False)
class IKEPolicyListView(generic.ObjectListView):
    queryset = IKEPolicy.objects.all()
    filterset = filtersets.IKEPolicyFilterSet
    filterset_form = forms.IKEPolicyFilterForm
    table = tables.IKEPolicyTable


@register_model_view(IKEPolicy)
class IKEPolicyView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = IKEPolicy.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.IKEPolicyPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            CommentsPanel(),
            TagsPanel(),
            RelatedObjectsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.ikeproposal',
                filters={'ike_policy_id': lambda ctx: ctx['object'].pk},
                title=_('Proposals'),
            ),
        ],
    )

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(IKEPolicy, 'add', detail=False)
@register_model_view(IKEPolicy, 'edit')
class IKEPolicyEditView(generic.ObjectEditView):
    queryset = IKEPolicy.objects.all()
    form = forms.IKEPolicyForm


@register_model_view(IKEPolicy, 'delete')
class IKEPolicyDeleteView(generic.ObjectDeleteView):
    queryset = IKEPolicy.objects.all()


@register_model_view(IKEPolicy, 'bulk_import', path='import', detail=False)
class IKEPolicyBulkImportView(generic.BulkImportView):
    queryset = IKEPolicy.objects.all()
    model_form = forms.IKEPolicyImportForm


@register_model_view(IKEPolicy, 'bulk_edit', path='edit', detail=False)
class IKEPolicyBulkEditView(generic.BulkEditView):
    queryset = IKEPolicy.objects.all()
    filterset = filtersets.IKEPolicyFilterSet
    table = tables.IKEPolicyTable
    form = forms.IKEPolicyBulkEditForm


@register_model_view(IKEPolicy, 'bulk_rename', path='rename', detail=False)
class IKEPolicyBulkRenameView(generic.BulkRenameView):
    queryset = IKEPolicy.objects.all()
    filterset = filtersets.IKEPolicyFilterSet


@register_model_view(IKEPolicy, 'bulk_delete', path='delete', detail=False)
class IKEPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = IKEPolicy.objects.all()
    filterset = filtersets.IKEPolicyFilterSet
    table = tables.IKEPolicyTable


#
# IPSec proposals
#

@register_model_view(IPSecProposal, 'list', path='', detail=False)
class IPSecProposalListView(generic.ObjectListView):
    queryset = IPSecProposal.objects.all()
    filterset = filtersets.IPSecProposalFilterSet
    filterset_form = forms.IPSecProposalFilterForm
    table = tables.IPSecProposalTable


@register_model_view(IPSecProposal)
class IPSecProposalView(generic.ObjectView):
    queryset = IPSecProposal.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.IPSecProposalPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            CommentsPanel(),
            TagsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.ipsecpolicy',
                filters={'ipsec_proposal_id': lambda ctx: ctx['object'].pk},
                title=_('IPSec Policies'),
            ),
        ],
    )


@register_model_view(IPSecProposal, 'add', detail=False)
@register_model_view(IPSecProposal, 'edit')
class IPSecProposalEditView(generic.ObjectEditView):
    queryset = IPSecProposal.objects.all()
    form = forms.IPSecProposalForm


@register_model_view(IPSecProposal, 'delete')
class IPSecProposalDeleteView(generic.ObjectDeleteView):
    queryset = IPSecProposal.objects.all()


@register_model_view(IPSecProposal, 'bulk_import', path='import', detail=False)
class IPSecProposalBulkImportView(generic.BulkImportView):
    queryset = IPSecProposal.objects.all()
    model_form = forms.IPSecProposalImportForm


@register_model_view(IPSecProposal, 'bulk_edit', path='edit', detail=False)
class IPSecProposalBulkEditView(generic.BulkEditView):
    queryset = IPSecProposal.objects.all()
    filterset = filtersets.IPSecProposalFilterSet
    table = tables.IPSecProposalTable
    form = forms.IPSecProposalBulkEditForm


@register_model_view(IPSecProposal, 'bulk_rename', path='rename', detail=False)
class IPSecProposalBulkRenameView(generic.BulkRenameView):
    queryset = IPSecProposal.objects.all()
    filterset = filtersets.IPSecProposalFilterSet


@register_model_view(IPSecProposal, 'bulk_delete', path='delete', detail=False)
class IPSecProposalBulkDeleteView(generic.BulkDeleteView):
    queryset = IPSecProposal.objects.all()
    filterset = filtersets.IPSecProposalFilterSet
    table = tables.IPSecProposalTable


#
# IPSec policies
#

@register_model_view(IPSecPolicy, 'list', path='', detail=False)
class IPSecPolicyListView(generic.ObjectListView):
    queryset = IPSecPolicy.objects.all()
    filterset = filtersets.IPSecPolicyFilterSet
    filterset_form = forms.IPSecPolicyFilterForm
    table = tables.IPSecPolicyTable


@register_model_view(IPSecPolicy)
class IPSecPolicyView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = IPSecPolicy.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.IPSecPolicyPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            CommentsPanel(),
            TagsPanel(),
            RelatedObjectsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                'vpn.ipsecproposal',
                filters={'ipsec_policy_id': lambda ctx: ctx['object'].pk},
                title=_('Proposals'),
            ),
        ],
    )

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(IPSecPolicy, 'add', detail=False)
@register_model_view(IPSecPolicy, 'edit')
class IPSecPolicyEditView(generic.ObjectEditView):
    queryset = IPSecPolicy.objects.all()
    form = forms.IPSecPolicyForm


@register_model_view(IPSecPolicy, 'delete')
class IPSecPolicyDeleteView(generic.ObjectDeleteView):
    queryset = IPSecPolicy.objects.all()


@register_model_view(IPSecPolicy, 'bulk_import', path='import', detail=False)
class IPSecPolicyBulkImportView(generic.BulkImportView):
    queryset = IPSecPolicy.objects.all()
    model_form = forms.IPSecPolicyImportForm


@register_model_view(IPSecPolicy, 'bulk_edit', path='edit', detail=False)
class IPSecPolicyBulkEditView(generic.BulkEditView):
    queryset = IPSecPolicy.objects.all()
    filterset = filtersets.IPSecPolicyFilterSet
    table = tables.IPSecPolicyTable
    form = forms.IPSecPolicyBulkEditForm


@register_model_view(IPSecPolicy, 'bulk_rename', path='rename', detail=False)
class IPSecPolicyBulkRenameView(generic.BulkRenameView):
    queryset = IPSecPolicy.objects.all()
    filterset = filtersets.IPSecPolicyFilterSet


@register_model_view(IPSecPolicy, 'bulk_delete', path='delete', detail=False)
class IPSecPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = IPSecPolicy.objects.all()
    filterset = filtersets.IPSecPolicyFilterSet
    table = tables.IPSecPolicyTable


#
# IPSec profiles
#

@register_model_view(IPSecProfile, 'list', path='', detail=False)
class IPSecProfileListView(generic.ObjectListView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    filterset_form = forms.IPSecProfileFilterForm
    table = tables.IPSecProfileTable


@register_model_view(IPSecProfile)
class IPSecProfileView(generic.ObjectView):
    queryset = IPSecProfile.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.IPSecProfilePanel(),
            TagsPanel(),
            CustomFieldsPanel(),
            CommentsPanel(),
        ],
        right_panels=[
            TemplatePanel('vpn/panels/ipsecprofile_ike_policy.html'),
            TemplatePanel('vpn/panels/ipsecprofile_ipsec_policy.html'),
        ],
    )


@register_model_view(IPSecProfile, 'add', detail=False)
@register_model_view(IPSecProfile, 'edit')
class IPSecProfileEditView(generic.ObjectEditView):
    queryset = IPSecProfile.objects.all()
    form = forms.IPSecProfileForm


@register_model_view(IPSecProfile, 'delete')
class IPSecProfileDeleteView(generic.ObjectDeleteView):
    queryset = IPSecProfile.objects.all()


@register_model_view(IPSecProfile, 'bulk_import', path='import', detail=False)
class IPSecProfileBulkImportView(generic.BulkImportView):
    queryset = IPSecProfile.objects.all()
    model_form = forms.IPSecProfileImportForm


@register_model_view(IPSecProfile, 'bulk_edit', path='edit', detail=False)
class IPSecProfileBulkEditView(generic.BulkEditView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    table = tables.IPSecProfileTable
    form = forms.IPSecProfileBulkEditForm


@register_model_view(IPSecProfile, 'bulk_rename', path='rename', detail=False)
class IPSecProfileBulkRenameView(generic.BulkRenameView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet


@register_model_view(IPSecProfile, 'bulk_delete', path='delete', detail=False)
class IPSecProfileBulkDeleteView(generic.BulkDeleteView):
    queryset = IPSecProfile.objects.all()
    filterset = filtersets.IPSecProfileFilterSet
    table = tables.IPSecProfileTable


#
# L2VPN
#

@register_model_view(L2VPN, 'list', path='', detail=False)
class L2VPNListView(generic.ObjectListView):
    queryset = L2VPN.objects.all()
    table = tables.L2VPNTable
    filterset = filtersets.L2VPNFilterSet
    filterset_form = forms.L2VPNFilterForm


@register_model_view(L2VPN)
class L2VPNView(generic.ObjectView):
    queryset = L2VPN.objects.all()
    layout = layout.Layout(
        layout.Row(
            layout.Column(
                panels.L2VPNPanel(),
                TagsPanel(),
                PluginContentPanel('left_page'),
            ),
            layout.Column(
                CustomFieldsPanel(),
                CommentsPanel(),
                PluginContentPanel('right_page'),
            ),
        ),
        layout.Row(
            layout.Column(
                ContextTablePanel('import_targets_table', title=_('Import Route Targets')),
            ),
            layout.Column(
                ContextTablePanel('export_targets_table', title=_('Export Route Targets')),
            ),
        ),
        layout.Row(
            layout.Column(
                ObjectsTablePanel(
                    'vpn.l2vpntermination',
                    filters={'l2vpn_id': lambda ctx: ctx['object'].pk},
                    actions=[
                        actions.AddObject(
                            'vpn.l2vpntermination',
                            url_params={'l2vpn': lambda ctx: ctx['object'].pk},
                            label=_('Add a Termination'),
                        ),
                    ],
                    title=_('Terminations'),
                ),
                PluginContentPanel('full_width_page'),
            ),
        ),
    )

    def get_extra_context(self, request, instance):
        import_targets_table = RouteTargetTable(
            instance.import_targets.prefetch_related('tenant'),
            orderable=False
        )
        import_targets_table.configure(request)
        export_targets_table = RouteTargetTable(
            instance.export_targets.prefetch_related('tenant'),
            orderable=False
        )
        export_targets_table.configure(request)

        return {
            'import_targets_table': import_targets_table,
            'export_targets_table': export_targets_table,
        }


@register_model_view(L2VPN, 'add', detail=False)
@register_model_view(L2VPN, 'edit')
class L2VPNEditView(generic.ObjectEditView):
    queryset = L2VPN.objects.all()
    form = forms.L2VPNForm


@register_model_view(L2VPN, 'delete')
class L2VPNDeleteView(generic.ObjectDeleteView):
    queryset = L2VPN.objects.all()


@register_model_view(L2VPN, 'bulk_import', path='import', detail=False)
class L2VPNBulkImportView(generic.BulkImportView):
    queryset = L2VPN.objects.all()
    model_form = forms.L2VPNImportForm


@register_model_view(L2VPN, 'bulk_edit', path='edit', detail=False)
class L2VPNBulkEditView(generic.BulkEditView):
    queryset = L2VPN.objects.all()
    filterset = filtersets.L2VPNFilterSet
    table = tables.L2VPNTable
    form = forms.L2VPNBulkEditForm


@register_model_view(L2VPN, 'bulk_rename', path='rename', detail=False)
class L2VPNBulkRenameView(generic.BulkRenameView):
    queryset = L2VPN.objects.all()
    filterset = filtersets.L2VPNFilterSet


@register_model_view(L2VPN, 'bulk_delete', path='delete', detail=False)
class L2VPNBulkDeleteView(generic.BulkDeleteView):
    queryset = L2VPN.objects.all()
    filterset = filtersets.L2VPNFilterSet
    table = tables.L2VPNTable


#
# L2VPN terminations
#

@register_model_view(L2VPNTermination, 'list', path='', detail=False)
class L2VPNTerminationListView(generic.ObjectListView):
    queryset = L2VPNTermination.objects.all()
    table = tables.L2VPNTerminationTable
    filterset = filtersets.L2VPNTerminationFilterSet
    filterset_form = forms.L2VPNTerminationFilterForm
    actions = (AddObject, BulkImport, BulkExport, BulkEdit, BulkDelete)


@register_model_view(L2VPNTermination)
class L2VPNTerminationView(generic.ObjectView):
    queryset = L2VPNTermination.objects.all()
    layout = layout.SimpleLayout(
        left_panels=[
            panels.L2VPNTerminationPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            TagsPanel(),
        ],
    )


@register_model_view(L2VPNTermination, 'add', detail=False)
@register_model_view(L2VPNTermination, 'edit')
class L2VPNTerminationEditView(generic.ObjectEditView):
    queryset = L2VPNTermination.objects.all()
    form = forms.L2VPNTerminationForm


@register_model_view(L2VPNTermination, 'delete')
class L2VPNTerminationDeleteView(generic.ObjectDeleteView):
    queryset = L2VPNTermination.objects.all()


@register_model_view(L2VPNTermination, 'bulk_import', path='import', detail=False)
class L2VPNTerminationBulkImportView(generic.BulkImportView):
    queryset = L2VPNTermination.objects.all()
    model_form = forms.L2VPNTerminationImportForm


@register_model_view(L2VPNTermination, 'bulk_edit', path='edit', detail=False)
class L2VPNTerminationBulkEditView(generic.BulkEditView):
    queryset = L2VPNTermination.objects.all()
    filterset = filtersets.L2VPNTerminationFilterSet
    table = tables.L2VPNTerminationTable
    form = forms.L2VPNTerminationBulkEditForm


@register_model_view(L2VPNTermination, 'bulk_delete', path='delete', detail=False)
class L2VPNTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = L2VPNTermination.objects.all()
    filterset = filtersets.L2VPNTerminationFilterSet
    table = tables.L2VPNTerminationTable
