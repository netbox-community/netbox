import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0020_standardize_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualmachine',
            name='vcpus',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
    ]
