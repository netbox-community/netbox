from django import forms
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin

OBJ_TYPE_CHOICES = (
    ('', _('All Objects')),
    (_('Circuits'), (
        ('provider', _('Providers')),
        ('circuit', _('Circuits')),
    )),
    (_('DCIM'), (
        ('site', _('Sites')),
        ('rack', _('Racks')),
        ('rackgroup', _('Rack Groups')),
        ('devicetype', _('Device types')),
        ('device', _('Devices')),
        ('virtualchassis', _('Virtual Chassis')),
        ('cable', _('Cables')),
        ('powerfeed', _('Power Feeds')),
    )),
    (_('IPAM'), (
        ('vrf', _('VRFs')),
        ('aggregate', _('Aggregates')),
        ('prefix', _('Prefixes')),
        ('ipaddress', _('IP addresses')),
        ('vlan', _('VLANs')),
    )),
    (_('Secrets'), (
        ('secret', _('Secrets')),
    )),
    (_('Tenancy'), (
        ('tenant', _('Tenants')),
    )),
    (_('Virtualization'), (
        ('cluster', _('Clusters')),
        ('virtualmachine', _('Virtual machines')),
    )),
)


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label=_('Search')
    )
    obj_type = forms.ChoiceField(
        choices=OBJ_TYPE_CHOICES, required=False, label=_('Type')
    )
