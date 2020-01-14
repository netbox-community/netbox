import django.db.models.deletion
from django.db import migrations, models

import ipam.fields


class Migration(migrations.Migration):

    replaces = [('ipam', '0003_ipam_add_vlangroups'), ('ipam', '0004_ipam_vlangroup_uniqueness'), ('ipam', '0005_auto_20160725_1842'), ('ipam', '0006_vrf_vlan_add_tenant'), ('ipam', '0007_prefix_ipaddress_add_tenant'), ('ipam', '0008_prefix_change_order'), ('ipam', '0009_ipaddress_add_status'), ('ipam', '0010_ipaddress_help_texts'), ('ipam', '0011_rir_add_is_private')]

    dependencies = [
        ('tenancy', '0001_initial'),
        ('dcim', '0010_devicebay_installed_device_set_null'),
        ('ipam', '0002_vrf_add_enforce_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='VLANGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vlan_groups', to='dcim.Site')),
            ],
            options={
                'ordering': ['site', 'name'],
                'unique_together': {('site', 'name'), ('site', 'slug')},
                'verbose_name': 'VLAN group',
                'verbose_name_plural': 'VLAN groups',
            },
        ),
        migrations.AddField(
            model_name='vlan',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='ipam.VLANGroup'),
        ),
        migrations.AlterModelOptions(
            name='vlan',
            options={'ordering': ['site', 'group', 'vid'], 'verbose_name': 'VLAN', 'verbose_name_plural': 'VLANs'},
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together={('group', 'vid'), ('group', 'name')},
        ),
        migrations.AddField(
            model_name='vlan',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AddField(
            model_name='vlan',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='tenancy.Tenant'),
        ),
        migrations.AddField(
            model_name='vrf',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vrfs', to='tenancy.Tenant'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='tenancy.Tenant'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='tenancy.Tenant'),
        ),
        migrations.AlterModelOptions(
            name='prefix',
            options={'ordering': ['vrf', 'family', 'prefix'], 'verbose_name_plural': 'prefixes'},
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Active'), (2, b'Reserved'), (5, b'DHCP')], default=1, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='address',
            field=ipam.fields.IPAddressField(help_text=b'IPv4 or IPv6 address (with mask)'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.OneToOneField(blank=True, help_text=b'The IP for which this address is the "outside" IP', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.IPAddress', verbose_name=b'NAT (Inside)'),
        ),
        migrations.AddField(
            model_name='rir',
            name='is_private',
            field=models.BooleanField(default=False, help_text=b'IP space managed by this RIR is considered private', verbose_name=b'Private'),
        ),
    ]
