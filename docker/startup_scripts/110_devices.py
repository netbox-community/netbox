import sys

from dcim.models import Site, Rack, DeviceRole, DeviceType, Device, Platform
from startup_script_utils import *
from tenancy.models import Tenant
from virtualization.models import Cluster

devices = load_yaml('/opt/netbox/initializers/devices.yml')

if devices is None:
  sys.exit()

required_assocs = {
  'device_role': (DeviceRole, 'name'),
  'device_type': (DeviceType, 'model'),
  'site': (Site, 'name')
}

optional_assocs = {
  'tenant': (Tenant, 'name'),
  'platform': (Platform, 'name'),
  'rack': (Rack, 'name'),
  'cluster': (Cluster, 'name')
}

for params in devices:
  custom_field_data = pop_custom_fields(params)

  # primary ips are handled later in `270_primary_ips.py`
  params.pop('primary_ip4', None)
  params.pop('primary_ip6', None)

  for assoc, details in required_assocs.items():
    model, field = details
    query = { field: params.pop(assoc) }

    params[assoc] = model.objects.get(**query)

  for assoc, details in optional_assocs.items():
    if assoc in params:
      model, field = details
      query = { field: params.pop(assoc) }

      params[assoc] = model.objects.get(**query)

  device, created = Device.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(device, custom_field_data)

    print("🖥️  Created device", device.name)
