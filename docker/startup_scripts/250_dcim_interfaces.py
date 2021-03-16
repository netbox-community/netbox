import sys

from dcim.models import Interface, Device
from startup_script_utils import *

interfaces = load_yaml('/opt/netbox/initializers/dcim_interfaces.yml')

if interfaces is None:
  sys.exit()

required_assocs = {
  'device': (Device, 'name')
}

for params in interfaces:
  custom_field_data = pop_custom_fields(params)

  for assoc, details in required_assocs.items():
    model, field = details
    query = { field: params.pop(assoc) }

    params[assoc] = model.objects.get(**query)

  interface, created = Interface.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(interface, custom_field_data)

    print("🧷 Created interface", interface.name, interface.device.name)
