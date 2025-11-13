import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0053_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='cable_position',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024),
                ],
            ),
        ),
    ]
