import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0060_denormalization_triggers'),
        ('dcim', '0251_fix_ltree_cascade_triggers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circuittermination',
            name='_location',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.location'
            ),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='_provider_network',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='circuits.providernetwork'
            ),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='_region',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.region'
            ),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.site'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='_site_group',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.sitegroup'
            ),
        ),
    ]
