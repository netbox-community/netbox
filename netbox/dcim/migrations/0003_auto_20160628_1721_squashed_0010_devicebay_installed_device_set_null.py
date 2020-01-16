import django.db.models.deletion
from django.db import migrations, models

import dcim.fields


def copy_primary_ip(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for d in Device.objects.select_related('primary_ip'):
        if not d.primary_ip:
            continue
        if d.primary_ip.family == 4:
            d.primary_ip4 = d.primary_ip
        elif d.primary_ip.family == 6:
            d.primary_ip6 = d.primary_ip
        d.save()


class Migration(migrations.Migration):

    replaces = [('dcim', '0003_auto_20160628_1721'), ('dcim', '0004_auto_20160701_2049'), ('dcim', '0005_auto_20160706_1722'), ('dcim', '0006_add_device_primary_ip4_ip6'), ('dcim', '0007_device_copy_primary_ip'), ('dcim', '0008_device_remove_primary_ip'), ('dcim', '0009_site_32bit_asn_support'), ('dcim', '0010_devicebay_installed_device_set_null')]

    dependencies = [
        ('ipam', '0001_initial'),
        ('dcim', '0002_auto_20160622_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[0, b'Virtual'], [800, b'10/100M (100BASE-TX)'], [1000, b'1GE (1000BASE-T)'], [1100, b'1GE (SFP)'], [1150, b'10GE (10GBASE-T)'], [1200, b'10GE (SFP+)'], [1300, b'10GE (XFP)'], [1400, b'40GE (QSFP+)']], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[0, b'Virtual'], [800, b'10/100M (100BASE-TX)'], [1000, b'1GE (1000BASE-T)'], [1100, b'1GE (SFP)'], [1150, b'10GE (10GBASE-T)'], [1200, b'10GE (SFP+)'], [1300, b'10GE (XFP)'], [1400, b'40GE (QSFP+)']], default=1200),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.NullBooleanField(choices=[(None, b'None'), (True, b'Parent'), (False, b'Child')], default=None, help_text=b'Parent devices house child devices in device bays. Select "None" if this device type is neither a parent nor a child.', verbose_name=b'Parent/child status'),
        ),
        migrations.CreateModel(
            name='DeviceBayTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_bay_templates', to='dcim.DeviceType')),
            ],
            options={
                'ordering': ['device_type', 'name'],
                'unique_together': {('device_type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='DeviceBay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_bays', to='dcim.Device')),
                ('installed_device', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_bay', to='dcim.Device')),
            ],
            options={
                'ordering': ['device', 'name'],
                'unique_together': {('device', 'name')},
            },
        ),
        migrations.AddField(
            model_name='interface',
            name='mac_address',
            field=dcim.fields.MACAddressField(blank=True, null=True, verbose_name=b'MAC Address'),
        ),
        migrations.AddField(
            model_name='device',
            name='primary_ip4',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ip4_for', to='ipam.IPAddress', verbose_name=b'Primary IPv4'),
        ),
        migrations.AddField(
            model_name='device',
            name='primary_ip6',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ip6_for', to='ipam.IPAddress', verbose_name=b'Primary IPv6'),
        ),
        migrations.RunPython(
            code=copy_primary_ip,
        ),
        migrations.RemoveField(
            model_name='device',
            name='primary_ip',
        ),
        migrations.AlterField(
            model_name='site',
            name='asn',
            field=dcim.fields.ASNField(blank=True, null=True, verbose_name=b'ASN'),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='installed_device',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_bay', to='dcim.Device'),
        ),
    ]
