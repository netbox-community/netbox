from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs, panels
from utilities.data import resolve_attr_path


class CircuitCircuitTerminationPanel(panels.ObjectPanel):
    """
    A panel showing the CircuitTermination assigned to the object.
    """

    template_name = 'circuits/panels/circuit_circuit_termination.html'
    title = _('Termination')

    def __init__(self, accessor=None, side=None, **kwargs):
        super().__init__(**kwargs)

        if accessor is not None:
            self.accessor = accessor
        if side is not None:
            self.side = side

    def get_context(self, context):
        return {
            **super().get_context(context),
            'side': self.side,
            'termination': resolve_attr_path(context, f'{self.accessor}.termination_{self.side.lower()}'),
        }


class CircuitGroupAssignmentsPanel(panels.ObjectsTablePanel):
    """
    A panel showing all Circuit Groups attached to the object.
    """

    title = _('Group Assignments')
    actions = [
        actions.AddObject(
            'circuits.CircuitGroupAssignment',
            url_params={
                'member_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'member': lambda ctx: ctx['object'].pk,
                'return_url': lambda ctx: ctx['object'].get_absolute_url(),
            },
            label=_('Assign Group'),
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(
            'circuits.CircuitGroupAssignment',
            filters={
                'member_type_id': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'member_id': lambda ctx: ctx['object'].pk,
            },
            **kwargs,
        )


class CircuitGroupPanel(panels.OrganizationalObjectPanel):
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')


class CircuitGroupAssignmentPanel(panels.ObjectAttributesPanel):
    group = attrs.RelatedObjectAttr('group', linkify=True)
    provider = attrs.RelatedObjectAttr('member.provider', linkify=True)
    member = attrs.GenericForeignKeyAttr('member', linkify=True)
    priority = attrs.ChoiceAttr('priority')


class CircuitPanel(panels.ObjectAttributesPanel):
    provider = attrs.RelatedObjectAttr('provider', linkify=True)
    provider_account = attrs.RelatedObjectAttr('provider_account', linkify=True)
    cid = attrs.TextAttr('cid', label=_('Circuit ID'), style='font-monospace', copy_button=True)
    type = attrs.RelatedObjectAttr('type', linkify=True, colored=True)
    status = attrs.ChoiceAttr('status')
    distance = attrs.NumericAttr('distance', unit_accessor='get_distance_unit_display')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    install_date = attrs.DateTimeAttr('install_date', spec='date')
    termination_date = attrs.DateTimeAttr('termination_date', spec='date')
    commit_rate = attrs.TemplatedAttr('commit_rate', template_name='circuits/circuit/attrs/commit_rate.html')
    description = attrs.TextAttr('description')


class CircuitTypePanel(panels.OrganizationalObjectPanel):
    color = attrs.ColorAttr('color')


class ProviderPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    asns = attrs.RelatedObjectListAttr('asns', linkify=True, label=_('ASNs'))
    description = attrs.TextAttr('description')


class ProviderAccountPanel(panels.ObjectAttributesPanel):
    provider = attrs.RelatedObjectAttr('provider', linkify=True)
    account = attrs.TextAttr('account', style='font-monospace', copy_button=True)
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class ProviderNetworkPanel(panels.ObjectAttributesPanel):
    provider = attrs.RelatedObjectAttr('provider', linkify=True)
    name = attrs.TextAttr('name')
    service_id = attrs.TextAttr('service_id', label=_('Service ID'), style='font-monospace', copy_button=True)
    description = attrs.TextAttr('description')


class VirtualCircuitTypePanel(panels.OrganizationalObjectPanel):
    color = attrs.ColorAttr('color')


class VirtualCircuitPanel(panels.ObjectAttributesPanel):
    provider = attrs.RelatedObjectAttr('provider', linkify=True)
    provider_network = attrs.RelatedObjectAttr('provider_network', linkify=True)
    provider_account = attrs.RelatedObjectAttr('provider_account', linkify=True)
    cid = attrs.TextAttr('cid', label=_('Circuit ID'), style='font-monospace', copy_button=True)
    type = attrs.RelatedObjectAttr('type', linkify=True, colored=True)
    status = attrs.ChoiceAttr('status')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')


class VirtualCircuitTerminationPanel(panels.ObjectAttributesPanel):
    provider = attrs.RelatedObjectAttr('virtual_circuit.provider', linkify=True)
    provider_network = attrs.RelatedObjectAttr('virtual_circuit.provider_network', linkify=True)
    provider_account = attrs.RelatedObjectAttr('virtual_circuit.provider_account', linkify=True)
    virtual_circuit = attrs.RelatedObjectAttr('virtual_circuit', linkify=True)
    role = attrs.ChoiceAttr('role')


class VirtualCircuitTerminationInterfacePanel(panels.ObjectAttributesPanel):
    title = _('Interface')

    device = attrs.RelatedObjectAttr('interface.device', linkify=True)
    interface = attrs.RelatedObjectAttr('interface', linkify=True)
    type = attrs.ChoiceAttr('interface.type')
    description = attrs.TextAttr('interface.description')
