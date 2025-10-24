import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0015_owner'),
        ('wireless', '0015_extend_wireless_link_abs_distance_upper_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='wirelesslan',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='wirelesslangroup',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='wirelesslink',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
    ]
