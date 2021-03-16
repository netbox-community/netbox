import sys

from startup_script_utils import *
from tenancy.models import Tenant, TenantGroup

tenants = load_yaml('/opt/netbox/initializers/tenants.yml')

if tenants is None:
  sys.exit()

optional_assocs = {
  'group': (TenantGroup, 'name')
}

for params in tenants:
  custom_field_data = pop_custom_fields(params)

  for assoc, details in optional_assocs.items():
    if assoc in params:
      model, field = details
      query = { field: params.pop(assoc) }

      params[assoc] = model.objects.get(**query)

  tenant, created = Tenant.objects.get_or_create(**params)

  if created:
    set_custom_fields_values(tenant, custom_field_data)

    print("👩‍💻 Created Tenant", tenant.name)
