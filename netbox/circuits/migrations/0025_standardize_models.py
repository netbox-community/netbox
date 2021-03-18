import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0024_standardize_name_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittype',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='provider',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
