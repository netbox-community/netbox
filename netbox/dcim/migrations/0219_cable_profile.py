import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0218_devicetype_device_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='cable',
            name='profile',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='position',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024),
                ],
            ),
        ),
        migrations.AlterModelOptions(
            name='cabletermination',
            options={'ordering': ('cable', 'cable_end', 'position', 'pk')},
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(
                fields=('cable', 'cable_end', 'position'),
                name='dcim_cabletermination_unique_position'
            ),
        ),
    ]
