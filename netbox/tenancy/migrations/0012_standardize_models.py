import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0011_standardize_name_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantgroup',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
