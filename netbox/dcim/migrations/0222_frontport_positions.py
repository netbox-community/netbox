import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0221_m2m_port_assignments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frontport',
            name='rear_port',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='rear_port_position',
        ),
        migrations.AddField(
            model_name='frontport',
            name='positions',
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024)
                ]
            ),
        ),
    ]
