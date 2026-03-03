from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0226_modulebay_rebuild_tree'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='config_context_data',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='config_context_data',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
    ]
