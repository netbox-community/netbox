from django.contrib.auth.models import Permission


def set_permissions(subject, permission_filters):
  if subject is None or permission_filters is None:
    return
  subject.clear()
  for permission_filter in permission_filters:
    if "*" in permission_filter:
      permission_filter_regex = "^" + permission_filter.replace("*", ".*") + "$"
      permissions = Permission.objects.filter(codename__iregex=permission_filter_regex)
      print("  ⚿ Granting", permissions.count(), "permissions matching '" + permission_filter + "'")
    else:
      permissions = Permission.objects.filter(codename=permission_filter)
      print("  ⚿ Granting permission", permission_filter)

    for permission in permissions:
      subject.add(permission)
