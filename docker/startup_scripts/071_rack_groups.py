from dcim.models import Site,RackGroup
from startup_script_utils import load_yaml
import sys

rack_groups = load_yaml('/opt/netbox/initializers/rack_groups.yml')

if rack_groups is None:
  sys.exit()

required_assocs = {
  'site': (Site, 'name')
}

for params in rack_groups:

  for assoc, details in required_assocs.items():
    model, field = details
    query = { field: params.pop(assoc) }
    params[assoc] = model.objects.get(**query)

  rack_group, created = RackGroup.objects.get_or_create(**params)

  if created:
    print("🎨 Created rack group", rack_group.name)
