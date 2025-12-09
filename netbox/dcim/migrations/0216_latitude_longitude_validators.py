import decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0215_rackreservation_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=8,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(decimal.Decimal('-90.0')),
                    django.core.validators.MaxValueValidator(decimal.Decimal('90.0'))
                ],
            ),
        ),
        migrations.AlterField(
            model_name='device',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(decimal.Decimal('-180.0')),
                    django.core.validators.MaxValueValidator(decimal.Decimal('180.0'))
                ],
            ),
        ),
        migrations.AlterField(
            model_name='site',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=8,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(decimal.Decimal('-90.0')),
                    django.core.validators.MaxValueValidator(decimal.Decimal('90.0'))
                ],
            ),
        ),
        migrations.AlterField(
            model_name='site',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(decimal.Decimal('-180.0')),
                    django.core.validators.MaxValueValidator(decimal.Decimal('180.0'))
                ],
            ),
        ),
    ]
