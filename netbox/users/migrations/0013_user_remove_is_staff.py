from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_drop_django_admin_log_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
