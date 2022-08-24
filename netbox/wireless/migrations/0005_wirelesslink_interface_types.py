from django.db import migrations, models
import django.db.models.deletion
import wireless.models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('wireless', '0004_wireless_tenancy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslink',
            name='interface_a',
            field=models.ForeignKey(limit_choices_to=wireless.models.get_wireless_interface_types, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface'),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='interface_b',
            field=models.ForeignKey(limit_choices_to=wireless.models.get_wireless_interface_types, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface'),
        ),
    ]
