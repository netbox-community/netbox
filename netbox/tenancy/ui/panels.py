from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class TenantGroupPanel(panels.NestedGroupObjectPanel):
    pass


class TenantPanel(panels.ObjectAttributesPanel):
    group = attrs.RelatedObjectAttr('group', linkify=True)
    description = attrs.TextAttr('description')


class ContactGroupPanel(panels.NestedGroupObjectPanel):
    pass


class ContactRolePanel(panels.OrganizationalObjectPanel):
    pass


class ContactPanel(panels.ObjectAttributesPanel):
    groups = attrs.TemplatedAttr('groups', label=_('Groups'), template_name='tenancy/attrs/groups.html')
    name = attrs.TextAttr('name')
    title = attrs.TextAttr('title')
    phone = attrs.TemplatedAttr('phone', label=_('Phone'), template_name='tenancy/attrs/phone.html')
    email = attrs.TemplatedAttr('email', label=_('Email'), template_name='tenancy/attrs/email.html')
    address = attrs.AddressAttr('address', map_url=False)
    link = attrs.TemplatedAttr('link', label=_('Link'), template_name='tenancy/attrs/link.html')
    description = attrs.TextAttr('description')
