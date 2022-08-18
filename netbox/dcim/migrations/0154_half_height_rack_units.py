import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0153_created_datetimefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='u_height',
            field=models.DecimalField(decimal_places=1, default=1.0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='device',
            name='position',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99.5)]),
        ),
    ]
