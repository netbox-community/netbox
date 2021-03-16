import sys

from dcim.models import Site
from ipam.models import Prefix, VLAN, Role, VRF
from netaddr import IPNetwork
from startup_script_utils import *
from tenancy.models import Tenant, TenantGroup

prefixes = load_yaml('/opt/netbox/initializers/prefixes.yml')

if prefixes is None:
  sys.exit()

optional_assocs = {
  'site': (Site, 'name'),
  'tenant': (Tenant, 'name'),
  'tenant_group': (TenantGroup, 'name'),
  'vlan': (VLAN, 'name'),
  'role': (Role, 'name'),
  'vrf': (VRF, 'name')
}

for params in prefixes:
  custom_field_data = pop_custom_fields(params)

  params['prefix'] = IPNetwork(params['prefix'])

  for assoc, details in optional_assocs.items():
    if assoc in params:
      model, field = details
      query = { field: params.pop(assoc) }
      params[assoc] = model.objects.get(**query)

  prefix, created = Prefix.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(prefix, custom_field_data)

    print("📌 Created Prefix", prefix.prefix)
