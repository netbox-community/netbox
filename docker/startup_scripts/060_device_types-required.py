import sys

from dcim.models import DeviceType, Manufacturer, Region
from startup_script_utils import *
from tenancy.models import Tenant

device_types = load_yaml('/opt/netbox/initializers/device_types.yml')

if device_types is None:
  sys.exit()

required_assocs = {
  'manufacturer': (Manufacturer, 'name')
}

optional_assocs = {
  'region': (Region, 'name'),
  'tenant': (Tenant, 'name')
}

for params in device_types:
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

  device_type, created = DeviceType.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(device_type, custom_field_data)

    print("🔡 Created device type", device_type.manufacturer, device_type.model)
