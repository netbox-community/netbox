from django.db import migrations, models


def update_content_types(apps, schema_editor):
    ObjectType = apps.get_model('core', 'ObjectType')
    ObjectPermission = apps.get_model('users', 'ObjectPermission')
    db_alias = schema_editor.connection.alias

    auth_group_ct = ObjectType.objects.using(db_alias).filter(app_label='auth', model='group').first()
    users_group_ct = ObjectType.objects.using(db_alias).filter(app_label='users', model='group').first()
    if auth_group_ct and users_group_ct:
        perms = ObjectPermission.objects.using(db_alias).filter(object_types__in=[auth_group_ct])
        for perm in perms:
            perm.object_types.remove(auth_group_ct)
            perm.object_types.add(users_group_ct)
            perm.save()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0008_flip_objectpermission_assignments'),
    ]

    operations = [
        # Update ContentTypes
        migrations.RunPython(code=update_content_types, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='objectpermission',
            name='object_types',
            field=models.ManyToManyField(related_name='object_permissions', to='core.objecttype'),
        ),
    ]
