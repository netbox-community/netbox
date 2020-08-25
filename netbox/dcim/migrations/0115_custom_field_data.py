import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0114_update_jsonfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='rack',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='site',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
