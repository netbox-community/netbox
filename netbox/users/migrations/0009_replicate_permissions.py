from django.db import migrations
from django.db.models import Q

ACTIONS = ['view', 'add', 'change', 'delete']


def replicate_permissions(apps, schema_editor):
    """
    Replicate all Permission assignments as ObjectPermissions.
    """
    Permission = apps.get_model('auth', 'Permission')
    ObjectPermission = apps.get_model('users', 'ObjectPermission')
    SecretRole = apps.get_model('secrets', 'SecretRole')

    # TODO: Optimize this iteration so that ObjectPermissions with identical sets of users and groups
    # are combined into a single ObjectPermission instance.
    for perm in Permission.objects.select_related('content_type'):
        if perm.codename.split('_')[0] in ACTIONS:
            action = perm.codename.split('_')[0]
        elif perm.codename == 'activate_userkey':
            action = 'change'
        elif perm.codename == 'run_script':
            action = 'run'
        else:
            action = perm.codename

        if perm.group_set.exists() or perm.user_set.exists():

            # Handle replication of SecretRole user/group assignments for Secrets
            if perm.codename == 'view_secret':
                for secretrole in SecretRole.objects.prefetch_related('users', 'groups'):
                    obj_perm = ObjectPermission(
                        name=f'{perm.content_type.app_label}.{perm.codename} ({secretrole.name})'[:100],
                        actions=[action],
                        constraints={'role__name': secretrole.name}
                    )
                    obj_perm.save()
                    obj_perm.object_types.add(perm.content_type)
                    # Assign only users/groups who both a) are assigned to the SecretRole and b) have the view_secret
                    # permission
                    obj_perm.groups.add(
                        *list(secretrole.groups.filter(permissions=perm))
                    )
                    obj_perm.users.add(*list(secretrole.users.filter(
                        Q(user_permissions=perm) | Q(groups__permissions=perm)
                    )))

            else:
                obj_perm = ObjectPermission(
                    # Copy name from original Permission object
                    name=f'{perm.content_type.app_label}.{perm.codename}'[:100],
                    actions=[action]
                )
                obj_perm.save()
                obj_perm.object_types.add(perm.content_type)

                if perm.group_set.exists():
                    obj_perm.groups.add(*list(perm.group_set.all()))
                if perm.user_set.exists():
                    obj_perm.users.add(*list(perm.user_set.all()))


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_objectpermission'),
    ]

    operations = [
        migrations.RunPython(
            code=replicate_permissions,
            reverse_code=migrations.RunPython.noop
        )
    ]
