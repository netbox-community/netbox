import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0221_m2m_port_assignments'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='frontport',
            name='dcim_frontport_unique_rear_port_position',
        ),
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
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024)
                ]
            ),
        ),
    ]
