import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0222_port_mappings'),
    ]

    operations = [
        # Remove rear_port & rear_port_position from FrontPortTemplate
        migrations.RemoveConstraint(
            model_name='frontporttemplate',
            name='dcim_frontporttemplate_unique_rear_port_position',
        ),
        migrations.RemoveField(
            model_name='frontporttemplate',
            name='rear_port',
        ),
        migrations.RemoveField(
            model_name='frontporttemplate',
            name='rear_port_position',
        ),

        # Add positions on FrontPortTemplate
        migrations.AddField(
            model_name='frontporttemplate',
            name='positions',
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024)
                ]
            ),
        ),

        # Remove rear_port & rear_port_position from FrontPort
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

        # Add positions on FrontPort
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
