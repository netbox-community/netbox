import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0236_moduletype_component_counts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='position',
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=4,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100.5)
                ]),
        ),
        migrations.AlterField(
            model_name='rack',
            name='starting_unit',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='racktype',
            name='starting_unit',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
