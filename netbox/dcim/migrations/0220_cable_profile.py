import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0219_devicetype_device_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='cable',
            name='profile',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='connector',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(256)
                ]
            ),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='positions',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(1024)
                    ]
                ),
                blank=True,
                null=True,
                size=None
            ),
        ),
        migrations.AlterModelOptions(
            name='cabletermination',
            options={'ordering': ('cable', 'cable_end', 'connector', 'pk')},  # connector may be null
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(
                fields=('cable', 'cable_end', 'connector'),
                name='dcim_cabletermination_unique_connector'
            ),
        ),
    ]
