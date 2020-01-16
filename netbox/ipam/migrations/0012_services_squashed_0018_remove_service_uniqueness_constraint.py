import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import ipam.fields


class Migration(migrations.Migration):

    replaces = [('ipam', '0012_services'), ('ipam', '0013_prefix_add_is_pool'), ('ipam', '0014_ipaddress_status_add_deprecated'), ('ipam', '0015_global_vlans'), ('ipam', '0016_unicode_literals'), ('ipam', '0017_ipaddress_roles'), ('ipam', '0018_remove_service_uniqueness_constraint')]

    dependencies = [
        ('dcim', '0022_color_names_to_rgb'),
        ('ipam', '0011_rir_add_is_private'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prefix',
            name='prefix',
            field=ipam.fields.IPNetworkField(help_text=b'IPv4 or IPv6 network with mask'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='role',
            field=models.ForeignKey(blank=True, help_text=b'The primary function of this prefix', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prefixes', to='ipam.Role'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Container'), (1, b'Active'), (2, b'Reserved'), (3, b'Deprecated')], default=1, help_text=b'Operational status of this prefix', verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Active'), (2, b'Reserved'), (3, b'Deprecated'), (5, b'DHCP')], default=1, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='dcim.Site'),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlan_groups', to='dcim.Site'),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='family',
            field=models.PositiveSmallIntegerField(choices=[(4, 'IPv4'), (6, 'IPv6')]),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='rir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aggregates', to='ipam.RIR', verbose_name='RIR'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='address',
            field=ipam.fields.IPAddressField(help_text='IPv4 or IPv6 address (with mask)'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='family',
            field=models.PositiveSmallIntegerField(choices=[(4, 'IPv4'), (6, 'IPv6')], editable=False),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.OneToOneField(blank=True, help_text='The IP for which this address is the "outside" IP', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.IPAddress', verbose_name='NAT (Inside)'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Reserved'), (3, 'Deprecated'), (5, 'DHCP')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='ipam.VRF', verbose_name='VRF'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='family',
            field=models.PositiveSmallIntegerField(choices=[(4, 'IPv4'), (6, 'IPv6')], editable=False),
        ),
        migrations.AddField(
            model_name='prefix',
            name='is_pool',
            field=models.BooleanField(default=False, help_text='All IP addresses within this prefix are considered usable', verbose_name='Is a pool'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='prefix',
            field=ipam.fields.IPNetworkField(help_text='IPv4 or IPv6 network with mask'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='role',
            field=models.ForeignKey(blank=True, help_text='The primary function of this prefix', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prefixes', to='ipam.Role'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Container'), (1, 'Active'), (2, 'Reserved'), (3, 'Deprecated')], default=1, help_text='Operational status of this prefix', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='vlan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.VLAN', verbose_name='VLAN'),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.VRF', verbose_name='VRF'),
        ),
        migrations.AlterField(
            model_name='rir',
            name='is_private',
            field=models.BooleanField(default=False, help_text='IP space managed by this RIR is considered private', verbose_name='Private'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Reserved'), (3, 'Deprecated')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='vid',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4094)], verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='enforce_unique',
            field=models.BooleanField(default=True, help_text='Prevent duplicate prefixes/IP addresses within this VRF', verbose_name='Enforce unique space'),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='rd',
            field=models.CharField(max_length=21, unique=True, verbose_name='Route distinguisher'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(10, 'Loopback'), (20, 'Secondary'), (30, 'Anycast'), (40, 'VIP'), (41, 'VRRP'), (42, 'HSRP'), (43, 'GLBP')], help_text='The functional role of this IP', null=True, verbose_name='Role'),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Reserved'), (3, 'Deprecated'), (5, 'DHCP')], default=1, help_text='The operational status of this IP', verbose_name='Status'),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
                ('protocol', models.PositiveSmallIntegerField(choices=[(6, 'TCP'), (17, 'UDP')])),
                ('port', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)], verbose_name='Port number')),
                ('description', models.CharField(blank=True, max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='dcim.Device', verbose_name='device')),
                ('ipaddresses', models.ManyToManyField(blank=True, related_name='services', to='ipam.IPAddress', verbose_name='IP addresses')),
            ],
            options={
                'ordering': ['device', 'protocol', 'port'],
                'unique_together': set(),
            },
        ),
    ]
