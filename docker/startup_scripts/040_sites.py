import sys

from dcim.models import Region, Site
from startup_script_utils import *
from tenancy.models import Tenant

sites = load_yaml('/opt/netbox/initializers/sites.yml')

if sites is None:
  sys.exit()

optional_assocs = {
  'region': (Region, 'name'),
  'tenant': (Tenant, 'name')
}

for params in sites:
  custom_field_data = pop_custom_fields(params)

  for assoc, details in optional_assocs.items():
    if assoc in params:
      model, field = details
      query = { field: params.pop(assoc) }

      params[assoc] = model.objects.get(**query)

  site, created = Site.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(site, custom_field_data)

    print("📍 Created site", site.name)
