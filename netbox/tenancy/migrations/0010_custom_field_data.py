import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0009_standardize_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
