import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0053_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='cable_connector',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(256)
                ],
            ),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable_positions',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(1024),
                    ]
                ),
                blank=True,
                null=True,
                size=None,
            ),
        ),
    ]
