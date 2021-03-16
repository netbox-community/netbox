import sys

from django.contrib.auth.models import User
from startup_script_utils import load_yaml, set_permissions
from users.models import Token

users = load_yaml('/opt/netbox/initializers/users.yml')
if users is None:
  sys.exit()

for username, user_details in users.items():
  if not User.objects.filter(username=username):
    user = User.objects.create_user(
      username = username,
      password = user_details.get('password', 0) or User.objects.make_random_password())

    print("👤 Created user",username)

    if user_details.get('api_token', 0):
      Token.objects.create(user=user, key=user_details['api_token'])

    yaml_permissions = user_details.get('permissions', [])
    set_permissions(user.user_permissions, yaml_permissions)
