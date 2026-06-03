from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0236_moduletype_component_counts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='local_context_data',
        ),
    ]
