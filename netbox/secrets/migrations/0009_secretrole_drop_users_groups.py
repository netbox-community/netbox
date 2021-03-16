from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secrets', '0008_standardize_description'),
        ('users', '0009_replicate_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='secretrole',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='secretrole',
            name='users',
        ),
    ]
