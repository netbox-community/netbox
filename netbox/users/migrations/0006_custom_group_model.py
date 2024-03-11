import users.models
from django.db import migrations, models


def update_custom_fields(apps, schema_editor):
    """
    Update any CustomFields referencing the old Group model to use the new model.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CustomField = apps.get_model('extras', 'CustomField')
    Group = apps.get_model('users', 'Group')

    if old_ct := ContentType.objects.filter(app_label='users', model='netboxgroup').first():
        new_ct = ContentType.objects.get_for_model(Group)
        CustomField.objects.filter(related_object_type=old_ct).update(related_object_type=new_ct)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_table'),
    ]

    operations = [
        # Create the new Group model & table
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('permissions', models.ManyToManyField(blank=True, related_name='groups', related_query_name='group', to='auth.permission')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            managers=[
                ('objects', users.models.NetBoxGroupManager()),
            ],
        ),

        # Copy existing groups from the old table into the new one
        migrations.RunSQL(
            "INSERT INTO users_group (SELECT id, name, '' AS description FROM auth_group)"
        ),

        # Update the sequence for group ID values
        migrations.RunSQL(
            "SELECT setval('users_group_id_seq', (SELECT MAX(id) FROM users_group))"
        ),

        # Update the "groups" M2M fields on User & ObjectPermission
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='users', related_query_name='user', to='users.group'),
        ),
        migrations.AlterField(
            model_name='objectpermission',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='object_permissions', to='users.group'),
        ),

        # Delete groups from the old table
        migrations.RunSQL(
            "DELETE from auth_group"
        ),

        # Update custom fields
        migrations.RunPython(
            code=update_custom_fields,
            reverse_code=migrations.RunPython.noop
        ),

        # Delete the proxy model
        migrations.DeleteModel(
            name='NetBoxGroup',
        ),
    ]
