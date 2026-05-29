import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0236_moduletype_component_counts'),
    ]

    def clear_legacy_0u_positions(apps, schema_editor):
        Device = apps.get_model('dcim', 'Device')
        Device.objects.filter(
            device_type__u_height=0,
            position=0,
        ).update(position=None)

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
        migrations.RunPython(clear_legacy_0u_positions, migrations.RunPython.noop),
    ]
