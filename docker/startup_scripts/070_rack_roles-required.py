from dcim.models import RackRole
from utilities.choices import ColorChoices

from startup_script_utils import load_yaml
import sys

rack_roles = load_yaml('/opt/netbox/initializers/rack_roles.yml')

if rack_roles is None:
  sys.exit()

for params in rack_roles:
  if 'color' in params:
    color = params.pop('color')

    for color_tpl in ColorChoices:
      if color in color_tpl:
        params['color'] = color_tpl[0]

  rack_role, created = RackRole.objects.get_or_create(**params)

  if created:
    print("🎨 Created rack role", rack_role.name)
