from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0052_gfk_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='config_context_data',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
    ]
