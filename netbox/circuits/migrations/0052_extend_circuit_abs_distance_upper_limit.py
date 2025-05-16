from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0051_virtualcircuit_group_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circuit',
            name='_abs_distance',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=13, null=True),
        ),
    ]
