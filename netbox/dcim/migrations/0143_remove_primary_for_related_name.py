from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0053_asn_model'),
        ('dcim', '0142_rename_128gfc_qsfp28'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='primary_ip4',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress'),
        ),
        migrations.AlterField(
            model_name='device',
            name='primary_ip6',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress'),
        ),
    ]
