import sys

from django.contrib.auth.models import Group, User
from startup_script_utils import load_yaml, set_permissions

groups = load_yaml('/opt/netbox/initializers/groups.yml')
if groups is None:
  sys.exit()

for groupname, group_details in groups.items():
  group, created = Group.objects.get_or_create(name=groupname)

  if created:
    print("👥 Created group", groupname)

  for username in group_details.get('users', []):
    user = User.objects.get(username=username)

    if user:
      user.groups.add(group)

  yaml_permissions = group_details.get('permissions', [])
  set_permissions(group.permissions, yaml_permissions)
