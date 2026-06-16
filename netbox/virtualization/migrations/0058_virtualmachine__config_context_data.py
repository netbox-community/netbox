from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0057_denormalization_triggers'),
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
        migrations.AddIndex(
            model_name='virtualmachine',
            index=models.Index(
                condition=models.Q(('_config_context_data__isnull', True)),
                fields=['id'],
                name='virtualization_vm_cc_null',
            ),
        ),
    ]
