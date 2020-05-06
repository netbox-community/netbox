from django.contrib.auth import get_user_model
from django.db import migrations


def create_userconfigs(apps, schema_editor):
    """
    Create an empty UserConfig instance for each existing User.
    """
    User = get_user_model()
    UserConfig = apps.get_model('users', 'UserConfig')
    UserConfig.objects.bulk_create(
        [UserConfig(user_id=user.pk) for user in User.objects.all()]
    )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userconfig'),
    ]

    operations = [
        migrations.RunPython(
            code=create_userconfigs,
            reverse_code=migrations.RunPython.noop
        ),
    ]
