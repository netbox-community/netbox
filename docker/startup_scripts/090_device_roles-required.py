from dcim.models import DeviceRole
from utilities.choices import ColorChoices

from startup_script_utils import load_yaml
import sys

device_roles = load_yaml('/opt/netbox/initializers/device_roles.yml')

if device_roles is None:
  sys.exit()

for params in device_roles:

  if 'color' in params:
    color = params.pop('color')

    for color_tpl in ColorChoices:
      if color in color_tpl:
        params['color'] = color_tpl[0]

  device_role, created = DeviceRole.objects.get_or_create(**params)

  if created:
    print("🎨 Created device role", device_role.name)
