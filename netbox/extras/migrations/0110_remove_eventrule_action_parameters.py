from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0109_script_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventrule',
            name='action_parameters',
        ),
        migrations.DeleteModel(
            name='ReportModule',
        ),
    ]
