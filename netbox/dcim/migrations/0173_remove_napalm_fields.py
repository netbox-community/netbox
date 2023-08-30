from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0172_larger_power_draw_values'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platform',
            name='napalm_args',
        ),
        migrations.RemoveField(
            model_name='platform',
            name='napalm_driver',
        ),
    ]
