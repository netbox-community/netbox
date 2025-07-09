import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0208_platform_manufacturer_uniqueness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='tx_power',
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-40),
                    django.core.validators.MaxValueValidator(127)
                ]
            ),
        ),
    ]
