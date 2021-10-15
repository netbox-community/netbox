from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0137_rename_cable_peer'),
        ('wireless', '0001_wireless'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='rf_role',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel_frequency',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel_width',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='wireless_lans',
            field=models.ManyToManyField(blank=True, related_name='interfaces', to='wireless.WirelessLAN'),
        ),
        migrations.AddField(
            model_name='interface',
            name='wireless_link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wireless.wirelesslink'),
        ),
    ]
