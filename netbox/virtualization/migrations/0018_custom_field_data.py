import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0017_update_jsonfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
