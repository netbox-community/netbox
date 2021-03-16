import sys

from dcim.models import Site, RackRole, Rack, RackGroup
from startup_script_utils import *
from tenancy.models import Tenant

racks = load_yaml('/opt/netbox/initializers/racks.yml')

if racks is None:
  sys.exit()

required_assocs = {
  'site': (Site, 'name')
}

optional_assocs = {
  'role': (RackRole, 'name'),
  'tenant': (Tenant, 'name'),
  'group': (RackGroup, 'name')
}

for params in racks:
  custom_field_data = pop_custom_fields(params)

  for assoc, details in required_assocs.items():
    model, field = details
    query = { field: params.pop(assoc) }

    params[assoc] = model.objects.get(**query)

  for assoc, details in optional_assocs.items():
    if assoc in params:
      model, field = details
      query = { field: params.pop(assoc) }

      params[assoc] = model.objects.get(**query)

  rack, created = Rack.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(rack, custom_field_data)

    print("🔳 Created rack", rack.site, rack.name)
