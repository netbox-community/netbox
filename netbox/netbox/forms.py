from django import forms

from utilities.forms import BootstrapMixin

OBJ_TYPE_CHOICES = (
    ('', 'All Objects'),
    ('Circuits', (
        ('provider', 'Providers'),
        ('circuit', 'Circuits'),
    )),
    ('DCIM', (
        ('site', 'Sites'),
        ('rack', 'Racks'),
        ('rackgroup', 'Rack Groups'),
        ('devicetype', 'Device Types'),
        ('device', 'Devices'),
        ('virtualchassis', 'Virtual Chassis'),
        ('cable', 'Cables'),
        ('powerfeed', 'Power Feeds'),
    )),
    ('IPAM', (
        ('vrf', 'VRFs'),
        ('aggregate', 'Aggregates'),
        ('prefix', 'Prefixes'),
        ('ipaddress', 'IP Addresses'),
        ('vlan', 'VLANs'),
    )),
    ('Secrets', (
        ('secret', 'Secrets'),
    )),
    ('Tenancy', (
        ('tenant', 'Tenants'),
    )),
    ('Virtualization', (
        ('cluster', 'Clusters'),
        ('virtualmachine', 'Virtual Machines'),
    )),
)

def build_options():
    options = [{"label": OBJ_TYPE_CHOICES[0][1], "items": []}]
    
    for label, choices in OBJ_TYPE_CHOICES[1:]:
        items = []
        
        for value, choice_label in choices:
            items.append({"label": choice_label, "value": value})    
        
        options.append({"label": label, "items": items })
    return options

class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label='Search'
    )
    obj_type = forms.ChoiceField(
        choices=OBJ_TYPE_CHOICES, required=False, label='Type'
    )
    options = build_options()
