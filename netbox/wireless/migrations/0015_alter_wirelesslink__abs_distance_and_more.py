from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0014_wirelesslangroup_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslink',
            name='_abs_distance',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='distance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True),
        ),
    ]
