from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0236_moduletype_component_counts'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='_config_context_data',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
    ]
