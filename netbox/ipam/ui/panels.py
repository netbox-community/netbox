from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, panels


class FHRPGroupAssignmentsPanel(panels.ObjectPanel):
    """
    A panel which lists all FHRP group assignments for a given object.
    """

    template_name = 'ipam/panels/fhrp_groups.html'
    title = _('FHRP Groups')
    actions = [
        actions.AddObject(
            'ipam.FHRPGroup',
            url_params={
                'return_url': lambda ctx: reverse(
                    'ipam:fhrpgroupassignment_add',
                    query={
                        'interface_type': ContentType.objects.get_for_model(ctx['object']).pk,
                        'interface_id': ctx['object'].pk,
                    },
                ),
            },
            label=_('Create Group'),
        ),
        actions.AddObject(
            'ipam.FHRPGroupAssignment',
            url_params={
                'interface_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'interface_id': lambda ctx: ctx['object'].pk,
            },
            label=_('Assign Group'),
        ),
    ]
