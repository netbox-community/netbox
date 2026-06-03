from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0056_virtualmachine_render_config_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='_config_context_data',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='_config_context_generation',
            field=models.PositiveBigIntegerField(default=0, editable=False),
        ),
    ]
