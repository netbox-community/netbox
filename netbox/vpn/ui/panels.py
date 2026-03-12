from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class TunnelGroupPanel(panels.OrganizationalObjectPanel):
    pass


class TunnelPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    status = attrs.ChoiceAttr('status')
    group = attrs.RelatedObjectAttr('group', linkify=True)
    description = attrs.TextAttr('description')
    encapsulation = attrs.ChoiceAttr('encapsulation')
    ipsec_profile = attrs.RelatedObjectAttr('ipsec_profile', linkify=True, label=_('IPSec profile'))
    tunnel_id = attrs.TextAttr('tunnel_id', label=_('Tunnel ID'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')


class TunnelTerminationPanel(panels.ObjectAttributesPanel):
    tunnel = attrs.RelatedObjectAttr('tunnel', linkify=True)
    role = attrs.ChoiceAttr('role')
    parent_object = attrs.RelatedObjectAttr(
        'termination.parent_object', linkify=True, label=_('Parent')
    )
    termination = attrs.RelatedObjectAttr('termination', linkify=True, label=_('Interface'))
    outside_ip = attrs.RelatedObjectAttr('outside_ip', linkify=True, label=_('Outside IP'))


class IKEProposalPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    authentication_method = attrs.ChoiceAttr('authentication_method', label=_('Authentication method'))
    encryption_algorithm = attrs.ChoiceAttr('encryption_algorithm', label=_('Encryption algorithm'))
    authentication_algorithm = attrs.ChoiceAttr('authentication_algorithm', label=_('Authentication algorithm'))
    group = attrs.ChoiceAttr('group', label=_('DH group'))
    sa_lifetime = attrs.TextAttr('sa_lifetime', label=_('SA lifetime (seconds)'))


class IKEPolicyPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    version = attrs.ChoiceAttr('version', label=_('IKE version'))
    mode = attrs.ChoiceAttr('mode')
    preshared_key = attrs.TemplatedAttr(
        'preshared_key',
        label=_('Pre-shared key'),
        template_name='vpn/attrs/preshared_key.html',
    )


class IPSecProposalPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    encryption_algorithm = attrs.ChoiceAttr('encryption_algorithm', label=_('Encryption algorithm'))
    authentication_algorithm = attrs.ChoiceAttr('authentication_algorithm', label=_('Authentication algorithm'))
    sa_lifetime_seconds = attrs.TextAttr('sa_lifetime_seconds', label=_('SA lifetime (seconds)'))
    sa_lifetime_data = attrs.TextAttr('sa_lifetime_data', label=_('SA lifetime (KB)'))


class IPSecPolicyPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    pfs_group = attrs.ChoiceAttr('pfs_group', label=_('PFS group'))


class IPSecProfilePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    mode = attrs.ChoiceAttr('mode')


class L2VPNPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    identifier = attrs.TextAttr('identifier')
    type = attrs.ChoiceAttr('type')
    status = attrs.ChoiceAttr('status')
    description = attrs.TextAttr('description')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True)


class L2VPNTerminationPanel(panels.ObjectAttributesPanel):
    l2vpn = attrs.RelatedObjectAttr('l2vpn', linkify=True, label=_('L2VPN'))
    assigned_object = attrs.RelatedObjectAttr('assigned_object', linkify=True, label=_('Assigned object'))
