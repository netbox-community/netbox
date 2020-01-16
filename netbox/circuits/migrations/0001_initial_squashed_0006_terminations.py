import django.db.models.deletion
from django.db import migrations, models

import dcim.fields


def circuits_to_terms(apps, schema_editor):
    Circuit = apps.get_model('circuits', 'Circuit')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    for c in Circuit.objects.all():
        CircuitTermination(
            circuit=c,
            term_side=b'A',
            site=c.site,
            interface=c.interface,
            port_speed=c.port_speed,
            upstream_speed=c.upstream_speed,
            xconnect_id=c.xconnect_id,
            pp_info=c.pp_info,
        ).save()


class Migration(migrations.Migration):

    replaces = [('circuits', '0001_initial'), ('circuits', '0002_auto_20160622_1821'), ('circuits', '0003_provider_32bit_asn_support'), ('circuits', '0004_circuit_add_tenant'), ('circuits', '0005_circuit_add_upstream_speed'), ('circuits', '0006_terminations')]

    dependencies = [
        ('tenancy', '0001_initial'),
        ('dcim', '0001_initial'),
        ('dcim', '0022_color_names_to_rgb'),
    ]

    operations = [
        migrations.CreateModel(
            name='CircuitType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('asn', dcim.fields.ASNField(blank=True, null=True, verbose_name=b'ASN')),
                ('account', models.CharField(blank=True, max_length=30, verbose_name=b'Account number')),
                ('portal_url', models.URLField(blank=True, verbose_name=b'Portal')),
                ('noc_contact', models.TextField(blank=True, verbose_name=b'NOC contact')),
                ('admin_contact', models.TextField(blank=True, verbose_name=b'Admin contact')),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Circuit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('cid', models.CharField(max_length=50, verbose_name=b'Circuit ID')),
                ('install_date', models.DateField(blank=True, null=True, verbose_name=b'Date installed')),
                ('port_speed', models.PositiveIntegerField(verbose_name=b'Port speed (Kbps)')),
                ('commit_rate', models.PositiveIntegerField(blank=True, null=True, verbose_name=b'Commit rate (Kbps)')),
                ('xconnect_id', models.CharField(blank=True, max_length=50, verbose_name=b'Cross-connect ID')),
                ('pp_info', models.CharField(blank=True, max_length=100, verbose_name=b'Patch panel/port(s)')),
                ('comments', models.TextField(blank=True)),
                ('interface', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='circuit', to='dcim.Interface')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.Provider')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='dcim.Site')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.CircuitType')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='tenancy.Tenant')),
                ('upstream_speed', models.PositiveIntegerField(blank=True, help_text=b'Upstream speed, if different from port speed', null=True, verbose_name=b'Upstream speed (Kbps)')),
            ],
            options={
                'ordering': ['provider', 'cid'],
                'unique_together': {('provider', 'cid')},
            },
        ),
        migrations.CreateModel(
            name='CircuitTermination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term_side', models.CharField(choices=[(b'A', b'A'), (b'Z', b'Z')], max_length=1, verbose_name='Termination')),
                ('port_speed', models.PositiveIntegerField(verbose_name=b'Port speed (Kbps)')),
                ('upstream_speed', models.PositiveIntegerField(blank=True, help_text=b'Upstream speed, if different from port speed', null=True, verbose_name=b'Upstream speed (Kbps)')),
                ('xconnect_id', models.CharField(blank=True, max_length=50, verbose_name=b'Cross-connect ID')),
                ('pp_info', models.CharField(blank=True, max_length=100, verbose_name=b'Patch panel/port(s)')),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='circuits.Circuit')),
                ('interface', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='circuit_termination', to='dcim.Interface')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='dcim.Site')),
            ],
            options={
                'ordering': ['circuit', 'term_side'],
                'unique_together': {('circuit', 'term_side')},
            },
        ),
        migrations.RunPython(
            code=circuits_to_terms,
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='interface',
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='port_speed',
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='pp_info',
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='site',
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='upstream_speed',
        ),
        migrations.RemoveField(
            model_name='circuit',
            name='xconnect_id',
        ),
    ]
