from django.db import migrations


def update_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    # Delete the new ContentTypes effected by the new models in the users app
    ContentType.objects.filter(app_label='users', model='user').delete()

    # Update the app labels of the original ContentTypes for auth.User to ensure
    # that any foreign key references are preserved
    ContentType.objects.filter(app_label='auth', model='user').update(app_label='users')

    netboxuser_ct = ContentType.objects.filter(app_label='users', model='netboxuser').first()
    if netboxuser_ct:
        user_ct = ContentType.objects.filter(app_label='users', model='user').first()
        CustomField = apps.get_model('extras', 'CustomField')
        CustomField.objects.filter(object_type_id=netboxuser_ct.id).update(object_type_id=user_ct.id)
        netboxuser_ct.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_squashed_0004'),
    ]

    operations = [
        # The User table was originally created as 'auth_user'. Now we nullify the model's
        # db_table option, so that it defaults to the app & model name (users_user). This
        # causes the database table to be renamed.
        migrations.AlterModelTable(
            name='user',
            table=None,
        ),

        # Rename auth_user_* sequences
        migrations.RunSQL("ALTER TABLE auth_user_groups_id_seq RENAME TO users_user_groups_id_seq"),
        migrations.RunSQL("ALTER TABLE auth_user_id_seq RENAME TO users_user_id_seq"),
        migrations.RunSQL("ALTER TABLE auth_user_user_permissions_id_seq RENAME TO users_user_user_permissions_id_seq"),

        # Rename auth_user_* indexes
        migrations.RunSQL("ALTER INDEX auth_user_pkey RENAME TO users_user_pkey"),
        # Hash is deterministic; generated via schema_editor._create_index_name()
        migrations.RunSQL("ALTER INDEX auth_user_username_6821ab7c_like RENAME TO users_user_username_06e46fe6_like"),
        migrations.RunSQL("ALTER INDEX auth_user_username_key RENAME TO users_user_username_key"),

        # Update ContentTypes
        migrations.RunPython(
            code=update_content_types,
            reverse_code=migrations.RunPython.noop
        ),
    ]
